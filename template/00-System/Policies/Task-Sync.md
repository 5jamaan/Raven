---
id: "ffb97e40-9f48-5049-b5e4-12b767bf0882"
type: "system"
privacy: "private"
ai_access: "allowed_when_relevant"
memory_eligible: false
source: "Kullanıcı"
created: "2026-09-12"
updated: "2026-09-12"
---

# Görev aynalama politikası

Obsidian ana kaynaktır. task_id UUID; Todoist remote ID ayrı SQLite eşlemesidir. Kısa content, due, genel alan etiketi ve UUID işareti gönderilir. Private başlık her zaman sabit ve ayrıntısızdır. Kaynak not gövdesi veya hassas başlığı gönderilmez.
Resmi Todoist OAuth plugin’i kullanılır; yerel token yoktur. claim gönderimden önce kalıcı pending kaydı oluşturur; başarılı remote ID ack ile yazılır. Aynı hash ve ok durumunda yeniden göndermez. Belirsiz sonuçta UUID ile Todoist’te arama yap; tekrar oluşturma. Todoist’ten dönüş başlangıçta öneri temellidir: kullanıcının mevcut notunu onaysız ezmeyen tek yönlü kaynak senkronizasyonu.
Inbox ve Today Todoist’in yerleşik görünümleridir. Düşük maliyet için tek RavenOS projesi altında Projeler, Profesyonel Gelişim, Kişisel, Beklenen Yanıtlar ve Değerlendirmeler bölümleri kullanılır. Proje/etiket adları özel içerikten türetilmez.
Hatırlatmayı tarih atamakla eş tutma. Eşlenmiş görev için push reminder oluştur ve iPhone’da Kullanıcı’tan doğrulama al. Plan kısıtı çıkarsa ücretli yükseltme yapma; kullanıcıya bildir.
[[00-System/Connections]]
