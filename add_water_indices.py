"""Derived water indices; original measurements are preserved unchanged."""
import csv
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent / 'Data'
SOURCE = ROOT / 'aquaculture_all_samples_sorted.csv'
OUTPUT = ROOT / 'aquaculture_with_derived_indices.csv'
METRICS = ['temperature', 'salinity', 'pH', 'DO', 'turbidity']

def oxygen_saturation(t_c, salinity):
    # USGS OWQ 2011.03, attachment equations 7 and 8.
    # At exactly 1 atm, the pressure correction factor is 1.
    k = t_c + 273.15
    fresh = math.exp(-139.34411 + 1.575701e5/k - 6.642308e7/k**2
                     + 1.243800e10/k**3 - 8.621949e11/k**4)
    salt_factor = math.exp(-salinity * (0.017674 - 10.754/k + 2140.7/k**2))
    return fresh * salt_factor

def number(row, key):
    if row.get(key, '') == '':
        return None
    value = float(row[key])
    return value if math.isfinite(value) else None

def fmt(value):
    return '' if value is None else f'{value:.6f}'

def main():
    with SOURCE.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        original_fields = list(reader.fieldnames)
        rows = list(reader)
    rows.sort(key=lambda r: (r['site'], r['device'], datetime.fromisoformat(r['ts'])))
    new_fields = [
        'assumed_atmospheric_pressure_kPa', 'input_units_status',
        'DO_saturation_mg_L', 'DO_saturation_percent', 'DO_deficit_mg_L',
        'DO_saturation_extrapolated_mg_L', 'DO_percent_extrapolated',
        'DO_deficit_extrapolated_mg_L', 'oxygen_calculation_status',
        'interval_minutes', 'rate_calculation_status',
    ] + [m + '_change_per_hour' for m in METRICS]
    previous = {}
    for row in rows:
        row.update({k: '' for k in new_fields})
        row['assumed_atmospheric_pressure_kPa'] = '101.325'
        row['input_units_status'] = 'assumed_temperature_degC_salinity_ppt_DO_mg_L_NOT_CONFIRMED'
        t, s, do = (number(row, key) for key in ['temperature','salinity','DO'])
        if row.get('sensor_error') or any(v is None for v in [t,s,do]):
            row['oxygen_calculation_status'] = 'missing_or_sensor_error'
        elif not (0 <= t <= 40) or s < 0 or do < 0:
            row['oxygen_calculation_status'] = 'invalid_or_outside_temperature_domain'
        else:
            sat = oxygen_saturation(t, s)
            values = [sat, 100*do/sat, sat-do]
            if s <= 40:
                keys = ['DO_saturation_mg_L','DO_saturation_percent','DO_deficit_mg_L']
                row['oxygen_calculation_status'] = 'within_USGS_domain_ASSUMED_UNITS_PRESSURE'
            else:
                keys = ['DO_saturation_extrapolated_mg_L','DO_percent_extrapolated','DO_deficit_extrapolated_mg_L']
                row['oxygen_calculation_status'] = 'salinity_gt_40_EXTRAPOLATION_NOT_VALIDATED'
            row.update({k: fmt(v) for k,v in zip(keys,values)})
        group = (row['site'], row['device'])
        prev = previous.get(group)
        if prev is None:
            row['rate_calculation_status'] = 'first_record'
        else:
            dt = (datetime.fromisoformat(row['ts'])-datetime.fromisoformat(prev['ts'])).total_seconds()
            row['interval_minutes'] = fmt(dt/60)
            if dt <= 0:
                status = 'nonpositive_interval'
            elif dt > 1800:
                status = 'gap_gt_30min_rates_blank'
            elif row.get('sensor_error') or prev.get('sensor_error'):
                status = 'sensor_error_current_or_previous'
            else:
                status = 'adjacent_difference_actual_elapsed_time'
                for m in METRICS:
                    a,b=number(prev,m),number(row,m)
                    if a is not None and b is not None:
                        row[m+'_change_per_hour'] = fmt((b-a)/(dt/3600))
            row['rate_calculation_status'] = status
        previous[group] = row
    rows.sort(key=lambda r: datetime.fromisoformat(r['ts']))
    with OUTPUT.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=original_fields+new_fields)
        writer.writeheader();writer.writerows(rows)
    with OUTPUT.open(encoding='utf-8-sig',newline='') as f:
        check=list(csv.DictReader(f))
    assert len(check)==len(rows)
    assert all(all(a[k]==b[k] for k in original_fields) for a,b in zip(rows,check))
    assert all(datetime.fromisoformat(a['ts'])<=datetime.fromisoformat(b['ts']) for a,b in zip(check,check[1:]))
    # Standard reference sanity checks and monotonic salinity effect.
    assert abs(oxygen_saturation(20,0)-9.09)<0.02
    assert abs(oxygen_saturation(0,0)-14.62)<0.03
    assert oxygen_saturation(25,35)<oxygen_saturation(25,0)
    for r in check:
        if r['DO_saturation_mg_L']:
            assert abs(float(r['DO_saturation_percent'])-100*float(r['DO'])/float(r['DO_saturation_mg_L']))<0.0001
    counts=Counter(r['oxygen_calculation_status'] for r in rows)
    notes='''# Các chỉ số bổ sung

Nguồn: aquaculture_all_samples_sorted.csv. Tệp gốc không bị sửa.

## Giả định bắt buộc
- temperature được giả định là °C, salinity là phần nghìn (ppt), DO là mg/L; dữ liệu nguồn chưa xác nhận đơn vị. Các kết quả vật lý chỉ có ý nghĩa khi giả định này đúng.
- Áp suất khí quyển giả định 101.325 kPa (1 atm), không phải áp suất thủy tĩnh tại độ sâu cảm biến.
- Thành phần ion nước được giả định tương tự nước biển. Không xác nhận cảm biến đã bù độ mặn đúng.

## Oxy
Theo USGS OWQ Technical Memorandum 2011.03, phương trình 7 và 8:
T = temperature + 273.15
DO0 = exp(-139.34411 + 157570.1/T - 66423080/T² + 12438000000/T³ - 862194900000/T⁴)
Fs = exp[-S(0.017674 - 10.754/T + 2140.7/T²)]
DO_saturation = DO0 × Fs (hệ số áp suất = 1 tại 1 atm).
DO_saturation_percent = 100 × DO / DO_saturation.
DO_deficit = DO_saturation - DO; âm có nghĩa vượt bão hòa, không cắt về 0.

DOTABLES công bố miền 0–40 °C, 0–40 ppt. Các cột chính chỉ được điền trong miền này.
Với salinity > 40, kết quả chỉ nằm ở ba cột có chữ extrapolated, cờ NOT_VALIDATED. Đây là ngoại suy tham khảo, không dùng làm số đo hoặc đầu vào điều khiển chưa kiểm chứng. Không cắt độ mặn về 40 và không âm thầm coi ngoại suy là hợp lệ.
Cả kết quả trong miền vẫn phụ thuộc đơn vị và áp suất giả định, không phải quan sát trực tiếp hay mức phù hợp cho một loài cá.

## Tốc độ biến đổi
Các cột *_change_per_hour = (giá trị hiện tại - giá trị liền trước) / số giờ thực giữa hai mẫu, tính riêng từng site/device. pH là đơn vị pH/giờ, temperature là °C/giờ; đơn vị độ đục chưa xác nhận nên là đơn vị nguồn/giờ. Đây là hiệu sai phân trung bình khoảng đo, không phải tốc độ tức thời hoặc dự báo.
Mẫu đầu, mẫu lỗi, mẫu ngay sau lỗi và khoảng gián đoạn > 30 phút để trống tốc độ. Mốc 30 phút là quy tắc xử lý dữ liệu của script, không phải ngưỡng sinh học. Không nội suy, không làm trơn, không tự loại bỏ spike.

## Chưa tính
- Khối lượng riêng: cần thống nhất thang độ mặn, áp suất/độ sâu và phương pháp phù hợp, đặc biệt với độ mặn cao.
- TSS: thiếu quan hệ hiệu chuẩn địa phương từ độ đục sang mg/L.
- Tỷ lệ NH3: chưa chốt mô hình cân bằng có hiệu chỉnh độ mặn cao; nồng độ NH3 còn cần TAN và quy ước đơn vị nitơ.
- CO2: thiếu thông số carbonate bổ sung như TA và thang pH.
- Điểm phù hợp môi trường: thiếu loài, giai đoạn và ngưỡng được xác nhận.
Không tạo giá trị giả cho các đại lượng trên.

## Nguồn phương pháp
https://water.usgs.gov/water-resources/software/DOTABLES/
https://water.usgs.gov/admin/memo/QW/qw11.03.pdf

Chạy lại: python add_water_indices.py
'''
    (ROOT/'derived_indices_README.md').write_text(notes,encoding='utf-8')
    print(json.dumps({'output':str(OUTPUT),'rows':len(rows),'added_columns':len(new_fields),'oxygen_status_counts':dict(counts),'rate_status_counts':dict(Counter(r['rate_calculation_status'] for r in rows))},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
