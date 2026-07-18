import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

void main() {
  runApp(const DefineAnalizApp());
}

class DefineAnalizApp extends StatelessWidget {
  const DefineAnalizApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Yapay Zeka Define İşaretleri',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.deepOrange,
        scaffoldBackgroundColor: const Color(0xFF121212),
        brightness: Brightness.dark,
      ),
      home: const AnaSayfa(),
    );
  }
}

class AnaSayfa extends StatefulWidget {
  const AnaSayfa({Key? key}) : super(key: key);

  @override
  State<AnaSayfa> createState() => _AnaSayfaState();
}

class _AnaSayfaState extends State<AnaSayfa> {
  File? _secilenGorsel;
  bool _yukleniyor = false;
  String _analizSonucu = "";

  final ImagePicker _picker = ImagePicker();

  // Bilgisayarının ev ağındaki güncel IP adresi tam olarak tanımlandı:
  final String baseUrl = "http://192.168.1.104:8000";

  Future<void> _gorselSec() async {
    try {
      final XFile? gorsel =
          await _picker.pickImage(source: ImageSource.gallery);
      if (gorsel != null) {
        setState(() {
          _secilenGorsel = File(gorsel.path);
          _analizSonucu =
              "Görsel seçildi. Analiz etmek için aşağıdaki butona basın.";
        });
      }
    } catch (e) {
      setState(() {
        _analizSonucu = "Görsel seçilirken hata oluştu: $e";
      });
    }
  }

  Future<void> _analizEt() async {
    if (_secilenGorsel == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Lütfen önce bir görsel seçin!")),
      );
      return;
    }

    setState(() {
      _yukleniyor = true;
      _analizSonucu = "Yapay zeka görseli analiz ediyor, lütfen bekleyin...";
    });

    try {
      var request =
          http.MultipartRequest('POST', Uri.parse('$baseUrl/analiz/isaret'));
      request.fields['soru'] = "Bu işaret nedir ve ne anlama gelir?";
      request.files
          .add(await http.MultipartFile.fromPath('file', _secilenGorsel!.path));

      var response = await request.send();
      var responseData = await http.Response.fromStream(response);

      if (response.statusCode == 200) {
        var decoded = jsonDecode(utf8.decode(responseData.bodyBytes));
        setState(() {
          _analizSonucu = decoded['analiz'] ?? "Analiz sonucu alınamadı.";
          _yukleniyor = false;
        });
      } else {
        setState(() {
          _analizSonucu =
              "Sunucu Hatası: ${response.statusCode}\n\nLütfen bilgisayarınızdaki Python backend sunucusunun (main.py) açık olduğunu kontrol edin.";
          _yukleniyor = false;
        });
      }
    } catch (e) {
      setState(() {
        _analizSonucu = "Bağlantı Hatası!\n\n"
            "Telefon, bilgisayardaki sunucuya ($baseUrl) ulaşamadı.\n\n"
            "Çözüm İçin Kontrol Et:\n"
            "1. Bilgisayar ve telefon aynı ev Wi-Fi ağına mı bağlı?\n"
            "2. Bilgisayarında Python sunucuyu 'uvicorn main:app --host 0.0.0.0 --port 8000' şeklinde mi başlattın?\n"
            "3. Windows Güvenlik Duvarı (Firewall) bağlantıyı engelliyor olabilir, gerekirse geçici olarak kapatıp tekrar dene.";
        _yukleniyor = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Yapay Zeka Arkeolojik İşaret Analizi'),
        backgroundColor: const Color(0xFF1F1F1F),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 10),
              // Görsel Önizleme Alanı
              Container(
                height: 250,
                decoration: BoxDecoration(
                  color: const Color(0xFF1F1F1F),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.deepOrange.withOpacity(0.5),
                    width: 2,
                  ),
                ),
                // BoxFit.contain ile görsel tam sığdırıldı, kırpılmayacak:
                child: _secilenGorsel != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: Image.file(
                          _secilenGorsel!,
                          fit: BoxFit.contain,
                        ),
                      )
                    : const Center(
                        child: Text(
                          "Analiz edilecek işareti yüklemek için dokunun",
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.grey),
                        ),
                      ),
              ),
              const SizedBox(height: 20),
              // Görsel Seçme Butonu
              ElevatedButton.icon(
                onPressed: _gorselSec,
                icon: const Icon(Icons.photo_library),
                label: const Text("Galeri / Kameradan Görsel Seç"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepOrange,
                  padding: const EdgeInsets.symmetric(vertical: 15),
                ),
              ),
              const SizedBox(height: 12),
              // Analiz Etme Butonu
              ElevatedButton.icon(
                onPressed: _yukleniyor ? null : _analizEt,
                icon: _yukleniyor
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      )
                    : const Icon(Icons.psychology),
                label: const Text("Yapay Zeka ile İşareti Çöz"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
                  padding: const EdgeInsets.symmetric(vertical: 15),
                ),
              ),
              const SizedBox(height: 25),
              // Sonuç Gösterim Paneli
              const Text(
                "Yapay Zeka Çözüm Raporu",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.deepOrange,
                ),
              ),
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E1E1E),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _analizSonucu.isEmpty
                      ? "Henüz bir analiz yapılmadı. Lütfen bir görsel seçip analiz başlatın."
                      : _analizSonucu,
                  style: const TextStyle(fontSize: 15, height: 1.4),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
