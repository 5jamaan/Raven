---
name: forget
description: "RavenOS’ta belirli bir bilgiyi unutma ve bağlı Mem0 kopyasını kaldırma isteğini hazırla."
---

# forget

Önce tam hedef not, kaynak UUID, Mem0 eşlemesi ve Git/yedek kopyalarının etkisini göster. Silme kapsamı için açık onay al. gateway.py mem0-forget --record <uuid> --approve-delete yalnız doğrulanmış eşlemeyi siler. Yeni bir forget talebi eski yedeklerin de temizlenmesine otomatik izin vermez.

Komutları vault kökünden ayarlardaki Python ile `00-System/Scripts/` altında çalıştır. Paylaşılan gizlilik ilkeleri için `00-System/Policies/Privacy.md`, kullanım için `START-HERE.md`.
