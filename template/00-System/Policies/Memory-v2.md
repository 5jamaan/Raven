---
id: "d73c4cf9-f869-5e72-bcef-52055a970369"
type: "policy"
privacy: "private"
ai_access: "allowed_when_relevant"
memory_eligible: false
source: "Kullanıcı — onaylanan Raven v2 tasarımı"
created: "2026-09-12"
updated: "2026-09-12"
---

# Raven v2 hafıza politikası

## Kapsam
Yalnız RavenOS klasöründe çalışan, kancası etkin Codex ve Claude Code oturumları.
Normal ChatGPT/Claude web sohbetleri, başka klasörler, araç çıktıları, gizli düşünme
izleri ve eski sohbet arşivleri otomatik taranmaz. Kayıt yeni kullanıcı mesajı ile
son görünür asistan yanıtıdır; tam konuşma dökümü Obsidian'a kopyalanmaz.

## Varsayılan ve istisna
Bu çalışma alanında kayıt kurulumda açıkça etkinleştirilirse açık. “Bu sohbeti kaydetme” veya [raven:off]
ilgili sohbet için yalnız kapatma anahtarı saklar; mesaj içeriğini kaydetmez.
“Dosya değiştirme”, “salt okunur”, “read-only” gibi açık ifadeler bulunan turlar
hiçbir yeni Raven kayıt dosyası oluşturmaz. Bu tür doğal dil eşleşmeleri güvenli
yönde atlayabilir; her olası ifade biçimini tanıdığı iddia edilmez. Kesin kontrol
için sohbet pause/resume veya memory.json içindeki genel enabled anahtarı kullanılır.
Plan modunda gelen turlar kaydedilmez. Kanca asistanı hiçbir zaman yeniden başlatmaz.

## Saklama ve dış işleme
Sır kalıpları diske yazılmadan maskelenir. Filtre tam bir hassas veri sınıflandırıcısı
değildir. Kayıtlar varsayılan private ve memory_eligible=false'dur.
Geçici içerik %LOCALAPPDATA%/RavenOS/Memory altında tutulur; başarılı özetlemede
kaldırılır, başarısız/bekleyen içerik en çok 3 gün sonraki bakımda temizlenir.
Bilgisayar kapalıyken bakım çalışamaz. Bu süre sağlayıcının kendi sohbet geçmişini
ve yedeklerini değiştirmez. Yedekler ham kuyruğu içermez.

Onaylanan ortak hafıza tasarımı kapsamında ilgili tur metni, ayarlanan Codex veya
Claude özetleyicisine gönderilebilir. Özetleyici ve model kurulumda açıkça seçilir. Claude
kaynağından gelen tur da seçilen özetleyici Codex ise OpenAI tarafından işlenir.
cloud_processing=false veya mevcut strict-local modu bu arka plan model gönderimini
durdurur. Sağlayıcı değiştirilince otomatik diğer sağlayıcıya düşülmez.
Mem0/Todoist politikası değişmedi: otomatik oturum özetleri bu servislere aktarılmaz.

## Bütçe
En çok 8 model çağrısı/gün, 96000 giriş karakteri/gün, çağrı başına 6 tur ve
16000 tur metni karakteri. Başarısız çağrı da bütçeden düşer; iş başına en çok iki
deneme. Son mesajdan en az 120 saniye beklenir. İşçi 15 dakikada bir çalışır.
8000 karakterden uzun kullanıcı mesajı veya toplamda 16000 karakteri aşan tur otomatik işlenmez; kanca uyarısı/durum incelemesi gerekir. Günlük kapasite en çok 48 turdur; yoğun kullanımda kuyruk ve süre aşımı izlenmelidir. 50 MB yerel kayıt sınırında yeni alım durur.
Bu sınırlar kesin ücret/kredi garantisi değildir; model sistem bağlamı ve çıktısı
ayrıca token tüketir. Dashboard sağlayıcının raporladığı kullanım değerini gösterir.

## Hafızanın anlamı
Otomatik özetler çıkarımdır, doğrulanmış gerçek değildir. Her anlamlı özet kaynak
konuşmacı ve birebir alıntı taşır. Asistan önerisi kullanıcı kararı yapılmaz.
Profil, kişisel tercih ve görev aynası otomatik değiştirilmez. Kaynak doğrulaması
alıntının varlığını doğrular; cümlenin gerçek dünyada doğru olduğunu kanıtlamaz.
Ortak konu bağlantıları olası ilişkidir, kesin anlamsal ilişki değildir.

## Dosyalar ve düzeltmeler
Sohbet kayıtları 85-Companion/Sessions; proje derlemeleri 60-Knowledge/Derived.
Başlangıçta yalnız ilgili proje özetleri yüklenir; eşleşmemişler general alanındadır.
Proje seçimi kullanıcı ifadesiyle bind aracına aktarılır; model gizlice eşlemez.
Üretilmiş not elle değiştirildiyse otomatik üstüne yazılmaz ve eski DB özeti
bağlama getirilmez. Notta ai_access=denied seçimi de erişimi durdurur.
Kullanıcı düzeltmesini kalıcı notta uygularken kaynağı koru; çelişkiyi sessizce ezme.

## Unutma
forget --session ... --confirm yalnız açık kullanıcı silme isteğiyle çalıştırılır.
Oturumun etkin hafıza kayıtlarını kaldırır, aynı kimliğin tekrar alınmasını engeller;
üretilmiş notta silindi işareti bırakır. Sağlayıcı geçmişi, kullanıcı kopyaları ve
önceki yedekler ayrıca yönetilmelidir. “Unuttum” derken kapsamı açıkça belirt.

[[00-System/Memory-Status]] · [[85-Companion/Memory-Index]]
