"""
Apa:
- panggil charstream, pake rules yang udah diload, jalanin dfa, ubah ke bentuk token

Ngapain:
- jalanin DFA per-karakter, ikutin rules
- setiap final state, map hasilnya ke bentuk token
- match symbol/token, kalo masi belum tentu, cek lookup table buat ngecek apakah hasilnya preserved word
- kalau invalid, misal ga ada transition untuk suatu karakter di state tertentu, raise/yield lexical error, sama keterangan yang jelas (line, col atau tambah deskripsi)

"""
