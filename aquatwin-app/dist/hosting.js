// Shared static preview cannot reach a visitor's local Ditto gateway.
const sharedPreview=!['localhost','127.0.0.1','::1','[::1]'].includes(location.hostname);
if(sharedPreview){
 const localDittoAction=dittoAction;
 dittoAction=async function(){
  dittoStatus={state:'unavailable',connected:false,message:'The shared site cannot connect to Ditto on a personal computer. Use the local app for gateway setup; observations and scenarios remain available here.'};
  render();
 };
 const workspaceRender=render;
 render=function(){
  workspaceRender();
  const footer=document.querySelector('footer');
  if(footer)footer.lastElementChild.textContent='Shared site · Logs and trial ranges are stored separately in each browser';
 };
}
