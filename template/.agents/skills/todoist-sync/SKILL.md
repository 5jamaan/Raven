---
name: todoist-sync
description: "RavenOS görevlerini resmi Todoist OAuth bağlantısıyla filtreli ve yinelenmesiz gönder."
---

# todoist-sync

Yalnız gateway.py preview --service todoist ile belirlenen notlar. Her not için gateway.py todoist-claim --input <not> kullan. duplicate-skipped ise gönderme. create/update sonucunda dönen tasks payloadını aynen resmi Todoist aracına ver; başlık, tarih veya açıklamaya kaynak nottan ek bilgi ekleme. Başarılı yanıtı gateway.py todoist-ack --record <uuid> --remote <id> --hash <hash> ile kaydet. Belirsiz sonuçta tekrar oluşturma; Todoist içinde UUID ile ara ve uzlaştır. Reminders yalnız eşlenmiş görev ID ve filtrelenmiş due tarihini kullanır. Tamamlanma dönüşü öneri olarak yeni yerel review notuna yazılır; mevcut görevi onaysız değiştirme. Proje/etiket/bölüm adları yalnız onaylı sabit Türkçe kategorilerdir.

Komutları vault kökünden ayarlardaki Python ile `00-System/Scripts/` altında çalıştır. Paylaşılan gizlilik ilkeleri için `00-System/Policies/Privacy.md`, kullanım için `START-HERE.md`.
