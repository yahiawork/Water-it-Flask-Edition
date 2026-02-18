function toggleDrawer(){
  const d = document.getElementById('drawer');
  if(!d) return;
  d.classList.toggle('open');
}

// close drawer on outside click
window.addEventListener('click', (e)=>{
  const d = document.getElementById('drawer');
  if(!d) return;
  const isOpen = d.classList.contains('open');
  if(!isOpen) return;
  const clickedInside = d.contains(e.target) || (e.target.closest && e.target.closest('.icon-btn'));
  if(!clickedInside) d.classList.remove('open');
});

function previewFiles(input){
  const preview = document.getElementById('preview');
  if(!preview) return;
  preview.innerHTML = '';
  const files = Array.from(input.files || []).slice(0,4);
  for(const f of files){
    const img = document.createElement('img');
    img.alt = 'preview';
    img.src = URL.createObjectURL(f);
    preview.appendChild(img);
  }
}

// -----------------------------
// Web Push Notifications
// -----------------------------

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

async function getVapidPublicKey(){
  const r = await fetch('/push/vapid-public-key');
  const j = await r.json();
  return (j.key || '').trim();
}

async function ensureServiceWorker(){
  if(!('serviceWorker' in navigator)) throw new Error('Service Worker not supported in this browser');
  return await navigator.serviceWorker.register('/static/js/sw.js');
}

async function subscribePush(){
  if(!('Notification' in window)) throw new Error('Notifications not supported in this browser');
  const perm = await Notification.requestPermission();
  if(perm !== 'granted') throw new Error('Permission not granted');

  const reg = await ensureServiceWorker();
  const key = await getVapidPublicKey();
  if(!key) throw new Error('Server VAPID_PUBLIC_KEY is missing. See README.');

  const sub = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(key)
  });

  const r = await fetch('/push/subscribe', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(sub)
  });
  const j = await r.json();
  if(!j.ok) throw new Error(j.error || 'Subscribe failed');
  return sub;
}

async function unsubscribePush(){
  const reg = await ensureServiceWorker();
  const sub = await reg.pushManager.getSubscription();
  if(!sub) return true;
  await fetch('/push/unsubscribe', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({endpoint: sub.endpoint})
  });
  await sub.unsubscribe();
  return true;
}

function setPushStatus(msg){
  const el = document.getElementById('pushStatus');
  if(el) el.textContent = msg;
}

window.addEventListener('DOMContentLoaded', ()=>{
  const en = document.getElementById('btnEnablePush');
  const dis = document.getElementById('btnDisablePush');
  if(en){
    en.addEventListener('click', async ()=>{
      try{
        setPushStatus('Enabling...');
        await subscribePush();
        setPushStatus('Enabled ✅ You will receive reminders as notifications.');
      }catch(e){
        setPushStatus('Failed: ' + (e && e.message ? e.message : String(e)));
      }
    });
  }
  if(dis){
    dis.addEventListener('click', async ()=>{
      try{
        setPushStatus('Disabling...');
        await unsubscribePush();
        setPushStatus('Disabled ✅');
      }catch(e){
        setPushStatus('Failed: ' + (e && e.message ? e.message : String(e)));
      }
    });
  }
});
