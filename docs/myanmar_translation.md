[Read in English](README.md)

# မြန်မာ ပဋိပက္ခ အချက်အလက် အမြင် စီမံကိန်း (Myanmar Conflict Insight Project)

မူလအစီအစဉ်အရ ဤစီမံကိန်းသည် မြန်မာနိုင်ငံအတွင်း ဖြစ်ပွားနေသော ပဋိပက္ခဆိုင်ရာ ဒေတာများကို ခွဲခြမ်းစိတ်ဖြာရန်နှင့် မြင်သာသော visualization များဖြင့် တင်ပြပေးနိုင်ရန်အတွက် အသုံးဝင်သော analytical toolkit နှင့် visualization hub တစ်ခုအဖြစ် တည်ဆောက်ထားခြင်းဖြစ်သည်။  
အဓိကရည်ရွယ်ချက်မှာ အကြမ်းဒေတာများ (raw data) ကို ရှင်းလင်းသော အချက်အလက်အမြင်များ (insights) နှင့် အသုံးပြုရလွယ်ကူသော visualization များအဖြစ် ပြောင်းလဲပေးရန် ဖြစ်သည်။

လက်ရှိအသုံးပြုနေသော အဓိကဒေတာကို **ACLED (Armed Conflict Location & Event Data Project)** မှ ရယူထားပြီး၊ ၂၀၂၁ ခုနှစ် ဖေဖော်ဝါရီ ၁ ရက်နေ့ စစ်တပ်အာဏာသိမ်းပြီးနောက်ကာလမှ စတင်သည့် အချိန်ကာလကို အထူးအာရုံစိုက်ထားသည်။

ဤစီမံကိန်း၏ ရည်ရွယ်ချက်မှာ သုတေသနပညာရှင်များ၊ သတင်းထောက်များ၊ အချက်အလက်ခွဲခြမ်းစိတ်ဖြာသူများအတွက် ပဋိပက္ခဖြစ်ပွားမှုလမ်းကြောင်းများ (conflict trends)၊ ပထဝီဝင်အရ အန္တရာယ်မြင့်နေရာများ (geographical hotspots) နှင့် ပါဝင်သည့်အဖွဲ့အစည်းများ၏ လှုပ်ရှားမှုအခြေအနေများ (actor dynamics) ကို ရှင်းလင်းစွာ မြင်နိုင်ရန် ပံ့ပိုးပေးခြင်း ဖြစ်သည်။  
ဒေတာများကိုလည်း မြေပြင်အခြေအနေ ပြောင်းလဲမှုများနှင့် ကိုက်ညီစေရန် ပုံမှန် အပ်ဒိတ်ပြုလုပ်သွားမည်ဖြစ်သည်။

---

## Project Status & Data Update

- **Start Date:** February 1, 2021 (Coup d'état)  
- **End Date:** Current Date (Rolling update)  

**Update Mechanism:**  
လက်ရှိတွင် ဒေတာများ၏ တိကျမှုနှင့် အရည်အသွေးကို ထိန်းသိမ်းရန် dataset ကို manual update ပြုလုပ်ထားသည်။  
စနစ်ကိုလည်း နောက်ထပ် data အသစ်များကို လွယ်ကူစွာ ထည့်သွင်းနိုင်ရန် ဒီဇိုင်းပြုလုပ်ထားသည်။

**Future Goal:**  
ACLED data များကို API သို့မဟုတ် scraper များမှတစ်ဆင့် အလိုအလျောက် ရယူခြင်းနှင့် cleaning လုပ်နိုင်သော script တစ်ခု ဖန်တီးရန် ရည်မှန်းထားပြီး၊ အချိန်နှင့်တပြေးညီ data accuracy ရရှိစေရန် ရည်ရွယ်ထားသည်။

---

ဤစီမံကိန်းသည် **Armed Conflict Location & Event Data Project (ACLED)** မှ ဒေတာများကို အသုံးပြုထားသည်။

- **Provider:** ACLED  
- **Location:** Myanmar  
- **Timeframe:** Feb 1, 2021 – Present  

**License:**  
ဤ repository အတွင်းရှိ analysis code များသည် open source ဖြစ်သည်။ သို့သော် ACLED data များသည် proprietary ဖြစ်သောကြောင့် raw data files များကို အသုံးပြုလိုပါက ACLED တွင် registration ပြုလုပ်ရမည်ဖြစ်သည်။  
ဤ repository သည် proprietary raw data files များကို ပြန်လည်ဖြန့်ဝေထားခြင်း မရှိပါ။

---

## Possibilities & Scope

ဤစီမံကိန်းသည် ရိုးရိုး data aggregation ထက် ကျော်လွန်ပြီး ပိုမိုနက်ရှိုင်းသော analysis များ ပြုလုပ်နိုင်ရန် ရည်ရွယ်ထားသည်။  
လက်ရှိတွင် စမ်းသပ်နေသော သို့မဟုတ် အကောင်အထည်ဖော်နေသော analysis အခွင့်အလမ်းများမှာ အောက်ပါအတိုင်း ဖြစ်သည်။

---

### 1. Temporal Analysis

- **Conflict Frequency:** နေ့စဉ် / အပတ်စဉ် / လစဉ် ဖြစ်ပွားသော conflict events အရေအတွက်ကို time-series graphs ဖြင့် ပြသခြင်း  
- **Fatality Trends:** အချိန်နှင့်အမျှ reported fatalities ပြောင်းလဲမှုများကို ခွဲခြမ်းစိတ်ဖြာ၍ အကြမ်းဖက်မှု မြင့်တက်သည့် အချိန်များကို ရှာဖွေခြင်း  
- **Event Typology:** ဖြစ်ရပ်အမျိုးအစားများကို ခွဲခြားတင်ပြခြင်း (ဥပမာ - Battles, Violence against civilians, Protests, Riots)

---

### 2. Geospatial Analysis

- **Conflict Hotspots:** ပဋိပက္ခဖြစ်ပွားသည့်နေရာများကို map ဖြင့်ပြသ၍ အန္တရာယ်မြင့်ဒေသများ (State/Region နှင့် Township အဆင့်) ကို ခွဲခြားသတ်မှတ်ခြင်း  
- **Displacement Correlation (Potential):** conflict data နှင့် IDP (Internally Displaced Persons) camp data များကို ပေါင်းစပ်ပြသ၍ လူရွှေ့ပြောင်းမှုများ ဖြစ်ပေါ်စေသော အကြောင်းရင်းများကို မြင်သာစေရန် visualization ပြုလုပ်ခြင်း  
- **Actor Control Zones:** လက်နက်ကိုင်အဖွဲ့အစည်းများ (Military/SAC, EAOs, PDFs) ၏ သက်ရောက်မှုဒေသများကို visualization ဖြင့် ပြသခြင်း

---

### 3. Actor Dynamics

- **Actor Interaction:** မည်သည့်အဖွဲ့များသည် မည်သည့်အဖွဲ့များနှင့် တိုက်ပွဲဝင်နေကြသည်ကို network graphs ဖြင့် ပြသခြင်း  
- **Most Active Actors:** conflict events များတွင် အများဆုံး ပါဝင်သည့် အဖွဲ့အစည်းများကို ranked list ဖြင့် ဖော်ပြခြင်း

---

### 4. Advanced Insights (Roadmap)

အတည်မပြုရသေးသော်လည်း၊ အခြေခံ Machine Learning နည်းပညာများကို စနစ်အတွင်း ပေါင်းစပ်အသုံးပြုနိုင်ရန် ရည်မှန်းထားသည်။

- **Natural Language Processing (NLP):** ACLED data ၏ "Notes" section ကို ခွဲခြမ်းစိတ်ဖြာ၍ incident များနှင့် သက်ဆိုင်သော keywords နှင့် sentiment များကို ထုတ်ယူခြင်း  
- **Predictive Modeling:** အချိန်စဉ် data များကို အသုံးပြု၍ အနီးအနားအနာဂတ်တွင် conflict intensity မည်သို့ ပြောင်းလဲနိုင်သည်ကို ခန့်မှန်းရန် time-series forecasting စမ်းသပ်ခြင်း

---

## Collaborators

- **Tain Yan Tun** — Data Engineer (Undergraduate)  
- **Kyaw Zay Aung** — Data Analyst (Undergraduate)

---

## Disclaimer & Ethics

ဤစီမံကိန်းတွင် ခွဲခြမ်းစိတ်ဖြာထားသော ဒေတာများသည် အမှန်တကယ်ဖြစ်ပွားနေသော အကြမ်းဖက်မှုများ၊ လူ့အခွင့်အရေးပြဿနာများနှင့် လူမှုဒုက္ခများနှင့် ဆက်စပ်နေသည်။  
ဤစီမံကိန်း၏ ရည်ရွယ်ချက်မှာ sensationalize လုပ်ရန် မဟုတ်ဘဲ သုတေသနအတွက် objective clarity ပေးရန် ဖြစ်သည်။

ACLED data များသည် မီဒီယာသတင်းများအပေါ် အခြေခံထားသဖြင့် ဖြစ်ရပ်အားလုံးကို မလုံလောက်စွာ ဖော်ပြနိုင်ခြင်း မရှိနိုင်ပါ။  
ထို့ကြောင့် visualization များ၏ တိကျမှုသည် မူလ data source အပေါ် မူတည်ပါသည်။

Raw data အတွက် အခွင့်အရေးအားလုံးသည် **ACLED** ထံတွင်သာ ပိုင်ဆိုင်သည်။  
ဤ repository အတွင်းရှိ analysis နှင့် code များကို **MIT License** အောက်တွင် ပေးထားပါသည်။

---

## License

ဤ repository အတွင်းရှိ code များကို **MIT License** အောက်တွင် လိုင်စင်ပေးထားပါသည်။  

Political violence နှင့် protest events ဆိုင်ရာ အချက်အလက်များကို **Armed Conflict Location & Event Data Project (ACLED)** မှ ရယူထားပါသည်။
