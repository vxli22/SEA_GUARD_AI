const translations = {
  ar:{tagline:"نظام ذكي لمراقبة البيئة البحرية",welcome:"حماية البحار تبدأ بالذكاء الاصطناعي",intro:"اكتشف النفايات البحرية وتابع مؤشرات جودة المياه من لوحة واحدة.",sensors:"قراءات الحساسات",turbidity:"العكارة",temperature:"درجة الحرارة",detect:"تحليل صورة بحرية",analyze:"تحليل الصورة",classes:"الفئات المستهدفة",modelNote:"يلزم وضع ملف best.pt بعد تدريب النموذج لتفعيل الكشف.",footer:"مشروع مراقبة البيئة البحرية"},
  en:{tagline:"Smart marine environment monitoring",welcome:"Protecting oceans with artificial intelligence",intro:"Detect marine litter and monitor water quality in one dashboard.",sensors:"Sensor readings",turbidity:"Turbidity",temperature:"Temperature",detect:"Analyze a marine image",analyze:"Analyze image",classes:"Target classes",modelNote:"Add your trained best.pt model to enable detection.",footer:"Marine environment monitoring project"}
};
let lang="ar";
document.getElementById("langBtn").onclick=()=>{lang=lang==="ar"?"en":"ar";document.documentElement.lang=lang;document.documentElement.dir=lang==="ar"?"rtl":"ltr";document.getElementById("langBtn").textContent=lang==="ar"?"EN":"AR";document.querySelectorAll("[data-i18n]").forEach(el=>el.textContent=translations[lang][el.dataset.i18n]);};
async function refreshSensors(){try{const r=await fetch("/api/sensors");const d=await r.json();for(const k of ["ph","tds","turbidity","temperature"])document.getElementById(k).textContent=d[k]??"—";document.getElementById("sensorTime").textContent=d.updated_at||"—";}catch(e){}}
refreshSensors();setInterval(refreshSensors,5000);
document.getElementById("detectForm").addEventListener("submit",async e=>{
 e.preventDefault();const file=document.getElementById("imageInput").files[0];if(!file)return;
 const msg=document.getElementById("detectMessage"),list=document.getElementById("results"),preview=document.getElementById("preview");
 preview.src=URL.createObjectURL(file);preview.hidden=false;list.innerHTML="";msg.textContent=lang==="ar"?"جارٍ التحليل...":"Analyzing...";
 const form=new FormData();form.append("image",file);
 try{const r=await fetch("/api/detect",{method:"POST",body:form});const d=await r.json();if(!r.ok)throw new Error(d.error||"Request failed");
 d.detections.forEach(x=>{const li=document.createElement("li");li.textContent=`${x.class} — ${(x.confidence*100).toFixed(1)}%`;list.appendChild(li);});
 msg.textContent=lang==="ar"?`تم العثور على ${d.detections.length} اكتشاف`:`${d.detections.length} detections found`;
 }catch(err){msg.textContent=err.message;}
});
