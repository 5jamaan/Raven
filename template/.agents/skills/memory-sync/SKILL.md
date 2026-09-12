---
name: memory-sync
description: "RavenOS seçilmiş shareable hafızalarını merkezi filtreyle Mem0’ya senkronize et."
---

# memory-sync

Önce gateway.py preview --service mem0. İlk aktarımda gerçek adayları ve brain.policy_hash değerini topluca göster; Kullanıcı’tan politika onayı al. Mem0 kimlik doğrulaması Windows Credential Manager içindedir. gateway.py mem0-test ekle/ara/sil testini önce doğrula. Onay kaydedilmeden mem0-sync çalışmaz. Policy hash değişirse yeniden onay. pending/reconcile kayıtlarını körlemesine tekrar gönderme.

Komutları vault kökünden ayarlardaki Python ile `00-System/Scripts/` altında çalıştır. Paylaşılan gizlilik ilkeleri için `00-System/Policies/Privacy.md`, kullanım için `START-HERE.md`.
