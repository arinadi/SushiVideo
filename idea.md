saya punya ide membuat ai video clipper dengan nama "SushiVideo". didalamnnya ada agent yang berperan sebagai sushi chef filosofinya adalah memotong bagian terbaik dari ikan untuk di sajikan dalam 1 gigitan. workflownya adalah
input :url youtube/video, subtitle.srt (optional)

process 1 : ambil video -> use subtitle / transcript (jika tidak ada) -> gemini api -> pilih beberapa segmen paling menarik.
output 1 : 1. csv list no/index, start, end, title, reason, caption. dan beberapa file_index.srt -> kirim semua file ke telegram.

proses 2 : setelah file terkirim agent melanjutkan proses edit video -> dengan menggunakan ffmpeg memotong video menjadi beberapa bagian sesuai dengan csv list, dipercepat 1.25x, jika video landscape maka akan dibuat video fitcenter ke portrait (no zoom, no crop) dengan background blur salah 1 frame video, buat subtitle hard sub dengan style yang mudah dibaca. dan output ditaruh di folder video_clipper.
output 2 : beberapa video clipper dengan title, dan hardcoded sub. -> kirim semua hasil ke telegram

pondasi teknis saya sudah punya D:\TTB, baca atau copy dan analisa jadikan refrensi utama.
buat arsitekturnya saya colab only. buang cpu support karena ini butuh gpu. use colab runtime. dan gunakan GPU default.
