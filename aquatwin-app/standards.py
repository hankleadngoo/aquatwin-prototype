"""AquaTwin application contracts, informed by ISO architecture patterns.

These are project rules, not verbatim ISO requirements or a conformance claim.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parent
PROFILE = json.loads((ROOT / 'dist' / 'architecture-profile.json').read_text(encoding='utf-8'))
LOCAL = timezone(timedelta(hours=7))


def validate_profile(profile):
    ids = [entity['id'] for entity in profile['entities']]
    if len(set(ids)) != len(ids) or ids.count(profile['target']['id']) != 1:
        raise ValueError('Target must resolve to exactly one registered entity')
    if not profile['twinId'] or set(profile['stateKinds']) != {'observed','estimated','predicted','simulated','desired'}:
        raise ValueError('Invalid twin identity or state-kind vocabulary')
    for relation in profile['relationships']:
        if relation['subject'] not in ids or relation['object'] not in ids:
            raise ValueError('Relationship references an unregistered entity')
        if relation['validFrom'] is not None or relation['validTo'] is not None:
            raise ValueError('Temporal assignments require an approved profile revision')
    if any(model['operationalUseAllowed'] or model['actuationAllowed'] for model in profile['models']):
        raise ValueError('This profile supports research models only')
    return profile


validate_profile(PROFILE)


def timestamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        result = result.replace(tzinfo=LOCAL)
    return result


def validate_observation(event):
    """Reject unmapped identities, units, non-finite values and cross-kind writes."""
    if not isinstance(event, dict):
        raise ValueError('Observation must be an object')
    for key in ['id', 'source', 'type', 'time', 'subject', 'data', 'schemaVersion']:
        if key not in event:
            raise ValueError('Missing envelope field: ' + key)
    payload = event['data']
    if not isinstance(payload, dict):
        raise ValueError('Invalid observation payload')
    for key in ['stateKind', 'targetId', 'siteId', 'sensorId', 'parameter', 'value',
                'unit', 'phenomenonTime', 'receivedAt', 'qualityFlag', 'sourceAuthority',
                'location', 'depthM', 'calibrationRef', 'provenance']:
        if key not in payload:
            raise ValueError('Missing payload field: ' + key)
    if event['schemaVersion'] != PROFILE['observationSchemaVersion'] or event['type'] != 'aquatwin.observation.v1':
        raise ValueError('Unsupported schema or event type')
    if event['subject'] != PROFILE['twinId'] or payload['targetId'] != PROFILE['target']['id']:
        raise ValueError('Unregistered twin or target')
    if (payload['siteId'], payload['sensorId']) != (PROFILE['siteId'], PROFILE['deviceId']):
        raise ValueError('Unregistered source identity')
    if payload['sourceAuthority'] != PROFILE['deviceId']:
        raise ValueError('Unexpected source authority')
    param = PROFILE['parameters'].get(payload['parameter'])
    if not param or payload['unit'] != param['unit']:
        raise ValueError('Unknown parameter or incorrect unit')
    if payload['stateKind'] != 'observed':
        raise ValueError('Only observed state may enter this observation contract')
    flag = payload['qualityFlag']
    if type(flag) is not int or flag not in [1, 2, 3, 4, 9]:
        raise ValueError('Invalid quality flag')
    value = payload['value']
    if value is not None and (type(value) not in [int, float] or not math.isfinite(value)):
        raise ValueError('Value must be finite or null')
    if (value is None) != (flag == 9):
        raise ValueError('Missing values must have flag 9; flag 9 must have null value')
    for key in ['time']:
        if timestamp(event[key]).utcoffset() is None:
            raise ValueError('Invalid time')
    if timestamp(event['time']) != timestamp(payload['phenomenonTime']):
        raise ValueError('Event time must equal phenomenon time')
    if payload['receivedAt'] is not None:
        timestamp(payload['receivedAt'])
    if not payload['provenance'].get('inputSnapshotId'):
        raise ValueError('Missing input snapshot provenance')
    # Site metadata is unknown in this release. Never invent it in an adapter.
    if any(payload[k] is not None for k in ['location', 'depthM', 'calibrationRef']):
        raise ValueError('Metadata requires an approved profile revision')
    expected_id = payload['provenance']['inputSnapshotId'] + ':' + payload['parameter']
    if event['id'] != expected_id:
        raise ValueError('Unexpected observation idempotency key')
    return event


def observations(data, cursor, quality):
    if type(cursor) is not int or not 0 <= cursor < len(data['rows']):
        raise ValueError('Invalid observation cursor')
    row = data['rows'][cursor]
    result = []
    for parameter, config in PROFILE['parameters'].items():
        event = {
            'schemaVersion': PROFILE['observationSchemaVersion'],
            'id': row['id'] + ':' + parameter,
            'source': 'urn:aquatwin:source:' + row['device'],
            'type': 'aquatwin.observation.v1', 'time': timestamp(row['ts']).isoformat(),
            'subject': PROFILE['twinId'],
            'data': {
                'stateKind': 'observed', 'targetId': PROFILE['target']['id'],
                'siteId': row['site'], 'sensorId': row['device'],
                'parameter': parameter, 'value': row['values'][parameter], 'unit': config['unit'],
                'phenomenonTime': timestamp(row['ts']).isoformat(), 'receivedAt': None,
                'qualityFlag': quality(cursor, parameter, cursor), 'sourceAuthority': row['device'],
                'location': None, 'depthM': None, 'calibrationRef': None,
                'provenance': {'inputSnapshotId': row['id'], 'sourceSnapshotSha256': data['meta']['sha256'],
                               'mappingVersion': PROFILE['mappingVersion'], 'qcVersion': data['meta']['qcVersion'],
                               'receivedAtStatus': 'unavailable_in_snapshot',
                               'sensorIdentityScope': 'acquisition_device_not_individual_probe'}
            }
        }
        result.append(validate_observation(event))
    return result


def health(source_time, now=None):
    now = now or datetime.now(timezone.utc)
    age = (now - timestamp(source_time)).total_seconds()
    future = age < 0
    return {'checkedAt': now.isoformat(), 'sourceTime': timestamp(source_time).isoformat(),
            'ageSeconds': age, 'staleAfterSeconds': PROFILE['synchronization']['staleAfterSeconds'],
            'stale': future or age > PROFILE['synchronization']['staleAfterSeconds'],
            'clockStatus': 'future_source_time' if future else 'source_clock_not_independently_verified',
            'operationalUseAllowed': False, 'mode': 'historical-replay'}


def enrich(snapshot, data, cursor, quality):
    events = observations(data, cursor, quality)
    snapshot['attributes'].update({'targetId': PROFILE['target']['id'],
        'architectureProfile': PROFILE['profileVersion'], 'stateContractVersion': PROFILE['observationSchemaVersion'],
        'stateKinds': PROFILE['stateKinds'], 'lifecycle': 'research-prototype'})
    for event in events:
        payload = event['data']
        snapshot['features'][payload['parameter']]['properties']['observed'].update({
            'stateKind': 'observed', 'eventId': event['id'], 'targetId': payload['targetId'],
            'phenomenonTime': payload['phenomenonTime'], 'receivedAt': None,
            'provenance': payload['provenance']})
    # Wall-clock freshness is computed on GET, never embedded in deduplicated snapshots.
    snapshot['features']['health']['properties']['freshnessEndpoint'] = '/api/state/health'
    return snapshot
