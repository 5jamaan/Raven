---
id: "83874ad5-83c4-5d47-8264-c87377c4a4c2"
type: "system"
privacy: "private"
ai_access: "allowed_when_relevant"
memory_eligible: false
source: "Kullanıcı"
created: "2026-09-12"
updated: "2026-09-12"
---

# Gizlilik politikası

İki kategori: private ve shareable. Sırlar üçüncü kategori değildir; kaydedilemez. Varsayılanlar Config/folder-policies.json; proje/klasör `_policy.json`; not Properties son istisnadır. Belirsizlik private. Başlık, dosya adı, kaynak ve payload birlikte taranır. Private notla bağlantı kurmak hedefi shareable yapmaz; her hedef ayrı doğrulanır.
Merkezi filtre brain.export_record; gerçek Mem0 gönderimi gateway; Todoist yalnız claim çıktısının aynen connector’a verilmesi. AGENTS doğrudan gönderimleri yasaklar. Bu bir işletim sistemi ağ güvenlik duvarı değildir; aynı kullanıcı yetkisiyle başka yazılım veya ajan dosyayı okuyup ağı kullanabilir. Kurulan yolun dışındaki davranış için mutlak teknik izolasyon iddia edilmez.
Sır filtresi bilinen token/anahtar kalıplarını ve hassas terimleri tarar. Bilinmeyen sır türlerini kusursuz saptamaz. Uzun rastgele değerler dış aktarımda engellenebilir. Yanlış pozitifleri filtreyi atlayarak çözme.
Private AI erişimi allowed_when_relevant; strict-local seçildiğinde başlangıç bağlamı private dosyaları atlar. Bulut modeli okuduğu private içeriği işleyebilir. Denetim günlükleri içerik değil UUID, hash, hedef ve durum taşır.
İlk Mem0 gerçek aktarımı toplu önizleme ve policy hash onayı ister. Politikalar veya filtre kodu değişirse yeniden onay. Hassas kişi/proje listesi Config/settings.json içindeki sensitive_terms alanıdır.
[[START-HERE]]
