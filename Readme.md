# GenAI Application

## Project Information
**Nama Project:**
Learning Material Generator API

**Use Case:**
Penganalisis dan Pembuat Bahan Ajar Otomatis Yang mudah di ingat dengan memberikan Keyword dan Kuis. 

**Deskripsi Singkat:**
API berbasis FastAPI yang memanfaatkan Gemini API untuk menerima teks materi pembelajaran lalu secara otomatis mengekstrak ringkasan, poin-poin utama, dan pertanyaan kuis.

## Tech Stack
* Python
* FastAPI
* Pydantic
* SDK `google-genai` (Gemini API)
* python-dotenv

## Application Flow
**User Input**
      ↓ 
 **FastAPI**
      ↓ 
 **LLM API** 
      ↓ 
**Structured Output**

1. **User Input**: Pengguna mengirimkan JSON berisi teks materi (`text`) dan target audiens (`target_audience`) melalui endpoint POST.
2. **FastAPI**: Aplikasi menerima request, melakukan validasi (memastikan input minimal 20 karakter menggunakan Pydantic), lalu menyusun prompt terstruktur (Role, Task, Context, Constraint, Output Format).
3. **LLM API**: Prompt dan skema output dikirimkan ke model `gemini-3.8-flash` melalui SDK `google-genai`. Model memproses teks dengan parameter `temperature` rendah (0.2) agar fokus pada fakta.
4. **Structured Output**: LLM mengembalikan respon dalam format JSON murni. FastAPI memparsing hasil tersebut dan meneruskannya kembali ke pengguna sebagai response API yang rapi dengan tiga field: `summary`, `key_points`, dan `quiz`.

## API Endpoint
`POST /analyze`

## Example Request
```json
{
  "text": "Prompt Engineering adalah teknik merancang instruksi agar LLM memberikan hasil yang akurat melalui berbagai teknik terstruktur.",
  "target_audience": "User"
}
```

## Example Response
```json
{
  "summary": "Prompt Engineering adalah teknik merancang instruksi terstruktur untuk LLM. Tujuannya adalah agar LLM dapat memberikan hasil yang akurat.",
  "key_points": [
    "Prompt Engineering merupakan teknik merancang instruksi.",
    "Instruksi dirancang untuk model LLM.",
    "Tujuan utamanya adalah memperoleh hasil yang akurat.",
    "Penerapannya dilakukan melalui berbagai teknik terstruktur."
  ],
  "quiz": [
    "Apa yang dimaksud dengan Prompt Engineering?",
    "Apa tujuan utama dari perancangan instruksi pada LLM dalam Prompt Engineering?",
    "Bagaimana cara instruksi dirancang dalam Prompt Engineering agar menghasilkan keluaran yang akurat?"
  ]
}
```

## Structured Output
Skema yang digunakan:
```json
{
  "summary": "string",
  "key_points": ["string", "string"],
  "quiz": ["string", "string"]
}
```
**Kenapa kalian memilih field-field tersebut?**
Karena fungsi utama aplikasi ini adalah mengubah teks panjang menjadi materi ajar interaktif. `summary` membantu pembaca mengerti garis besar, `key_points` membantu mereka fokus pada detail esensial, dan `quiz` digunakan sebagai alat ukur pemahaman secara langsung.

## Prompt Experiment
**Input yang Digunakan:**
"Prompt Engineering adalah teknik merancang dan mengoptimalkan instruksi agar Model Bahasa Besar (LLM) memberikan hasil yang akurat. Terdapat beberapa teknik utama dalam Prompt Engineering, yaitu Zero-Shot Prompting, Few-Shot Prompting, dan Chain-of-Thought. Penggunaan prompt yang terstruktur membantu AI memahami konteks, batasan, serta format output yang diinginkan secara lebih efektif."

### Prompt A
**Tuliskan prompt yang digunakan:**
`Rangkum teks berikut: [Teks Input]`

**Actual Output A:**
"Prompt Engineering adalah teknik optimasi instruksi untuk LLM agar menghasilkan respon akurat melalui teknik seperti Zero-Shot, Few-Shot, dan Chain-of-Thought."

### Prompt B
**Tuliskan prompt yang digunakan:**
System: `Anda adalah Asisten Edukasi AI.`
User: 
`[TASK] Buatlah ringkasan ringkas dari materi yang diberikan.`
`[CONTEXT] Target Audiens: Mahasiswa Teknik Informatika.`
`Materi Input: [Teks Input]`

**Actual Output B:**
"Sebagai bahan belajar Mahasiswa IT, Prompt Engineering merupakan metode penyusunan instruksi LLM menggunakan teknik Zero-Shot, Few-Shot, dan Chain-of-Thought agar output sistem lebih akurat."

### Prompt C
**Tuliskan prompt yang digunakan:**
System: `Anda adalah Asisten Edukasi AI yang ahli dalam menganalisis dan menyederhanakan materi pembelajaran.`
User: 
`[TASK] Buatlah bahan belajar terstruktur dari materi yang diberikan.`
`[CONTEXT] Target Audiens: Mahasiswa Teknik Informatika. Materi Input: [Teks Input]`
`[CONSTRAINT] 1. Rangkuman dibuat singkat (maksimal 2 kalimat). 2. Ekstrak poin utama maksimal 5 poin. 3. Buat tepat 3 pertanyaan kuis. 4. Gunakan bahasa edukatif.`
`[OUTPUT FORMAT] JSON sesuai dengan skema output.`

**Actual Output C:**
*(Menghasilkan JSON terstruktur berisi summary, key_points, dan quiz persis sesuai format skema Pydantic)*

## Prompt Evaluation
**Mana yang menurut kalian menghasilkan output paling baik?**
Prompt C.

**Kenapa?**
Karena outputnya sudah terstruktur rapi ke dalam JSON sehingga bisa langsung dikonsumsi oleh aplikasi frontend atau sistem lain. Selain itu, isinya terukur dan dapat diprediksi karena adanya *constraint* yang jelas.

**Apa perbedaan paling terlihat antara Prompt A, Prompt B, dan Prompt C berdasarkan hasil testing kalian?**
Prompt A menghasilkan paragraf naratif polos; Prompt B menyesuaikan gaya bahasa namun masih berupa narasi bebas; sementara Prompt C menghasilkan struktur data (JSON) yang ketat mematuhi jumlah poin, jumlah kalimat, dan format yang diminta.

## Failure Case
**Input yang menghasilkan output kurang baik:**
`"Python adalah bahasa pemrograman."`

**Actual Output:**
AI mengembalikan Output di mana ia berhalusinasi menambahkan informasi di luar teks(conteks), seperti klaim bahwa "Python sangat populer dan mudah dipelajari oleh pemula" demi memenuhi target 5 poin dan 3 kuis.

**Menurut kalian apa masalah dari output tersebut?**
Teks input terlalu pendek dan kekurangan konteks, sementara constraint prompt di awal tidak secara tegas melarang AI menggunakan pengetahuan di luar (eksternal) dari teks input.

**Apa yang kalian ubah pada prompt / constraint / kode?**
1. Menambahkan validasi di Pydantic agar menolak teks yang terlalu singkat.
2. Memperbarui constraint prompt menjadi: "HANYA gunakan informasi yang secara eksplisit ada pada teks input. DILARANG MENAMBAHKAN ATAU MENGARANG FAKTA LUAR".
3. Menurunkan temperature ke 2 agar AI tidak terlalu imajinatif.

**Output setelah diperbaiki:**
Teks yang kurang dari 20 karakter otomatis ditolak dengan status HTTP 422. Jika teksnya cukup panjang namun spesifik, AI merespons sangat faktual dan hanya mengekstrak fakta asli tanpa mengarang.

## Personal Reflection
**1. Menurut kalian, bagian apa yang paling sulit dari project ini?**
Mengatasi masalah Halusinasi yang Membuat AI selalu tidak Menurut atau mengarang, Jadi solusinya adalah memberikan Prompt yang jelas dan Tegas.

**2. Bagian kode mana yang paling banyak dibantu oleh AI?**
Bagian pembuatan Pydantic yang disinkronkan dengan skema GenerateContentConfig, serta penulisan *try-except* error handling.

**3. Setelah melihat kode tersebut, jelaskan menggunakan bahasa kalian sendiri bagaimana bagian tersebut bekerja.**
Kode tersebut bekerja dengan mendefinisikan bentuk JSON di awal. Kelas ini lalu disisipkan ke parameter response_schema saat memanggil SDK Gemini.lalu API Gemini dipaksa membalas bukan dengan teks biasa, melainkan string JSON murni yang sesuai bentuk tersebut, sehingga bisa langsung menganalisis menjadi response API FastAPI.

**4. Menurut kalian, apa kekurangan terbesar dari aplikasi yang kalian buat jika digunakan oleh user sungguhan?**
Tetusaja Tampilan UI/UX, dan kemmampuan untuk membaca file seperti word dan generate word/pdf

**5. Jika provider LLM kalian diganti, misalnya dari Groq ke Gemini atau OpenAI, bagian mana dari project yang menurut kalian perlu diubah?**
Inisialisasi Client SDK dan pemanggilan fungsi generasinya. Tiap SDK memiliki parameter pemanggilan dan penempatan. yang berbeda untuk menerapkan Structured Output.

**6. Setelah mencoba aplikasi kalian sendiri, apa satu improvement yang menurut kalian paling penting jika project ini dilanjutkan?**
Menambahkan fitur untuk membaca dokumen (PDF/Word), lalu user bisa meminta word/pdf tentu ini mungkin jikan ingin menambahkan fitur membuat soal bukan quiz yang nantinya bisa digunkan untuk guru/dosen untuk membuat soal yang menguji/mendidik (ininya soal berkualitas).

## AI Usage
**AI tools yang digunakan:**
Gemini

**AI digunakan untuk membantu bagian apa?**
Membantu saya memperbaiki code atau kesalahan ketik(Typo), Membantu merancang struktur Structured Output, memecahkan error Internal Server Error, dan menulis sebagian README.

**Bagian apa yang kalian tentukan, perbaiki, atau ubah sendiri setelah melihat hasil dari AI?**
Saya menentukan sendiri tema aplikasinya karena saya ingin aplikasi untuk membantu saya mengingat materi, menyiapkan input testing, dan mengubah alur validasi aplikasi agar menolak input yang terlalu pendek.
