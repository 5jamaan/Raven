---
name: history-import
description: "Kullanıcı’ın seçtiği konuşma dışa aktarımını yerelde inceleyip kısa not adaylarına dönüştür."
---

# history-import

Yalnız kullanıcının belirttiği dosyayı oku. Dosyanın tamamını hafızaya yükleme veya kopyalama. Yerelde rol/tarih ayrımı yap; açık düzeltme, karar, görev ve uzun vadeli bağlam adaylarını ayrı çıkar. Sırları ön taramayla dışla. Private varsayılanlı tarihli aday notlarını UUID ve kaynak hash ile yeni oluştur; kaynak dosyayı değiştirme. Özeti kullanıcıya göster; mevcut profile otomatik gerçek ekleme ve dışa aktarım yapma.

Komutları vault kökünden ayarlardaki Python ile `00-System/Scripts/` altında çalıştır. Paylaşılan gizlilik ilkeleri için `00-System/Policies/Privacy.md`, kullanım için `START-HERE.md`.
