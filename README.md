# Tugas Besar II3160 - Microservice Deployment: Perfume Recommendation
Nama: Tara Chandani Haryono  
NIM: 18221146

# Core Service
Core Service yang diimplementasikan dalam microservice Perfume Recommendation merupakan algoritma yang akan membantu pengguna untuk mendapat rekomendasi parfum sesuai dengan notes (wangi) yang diinginkan pengguna.
Algoritma akan mengembalikan daftar parfum yang memiliki kombinasi semua notes yang diinginkan pengguna.

# Teknologi yang digunakan
- fastapi 0.104.1  
- pydantic 2.4.2  
- uvicorn 0.24.0

# Cara Menjalankan Program
1. Akses `20.24.171.219/docs`
2. Menggunakan API endpoint yang ada di situs tersebut menekan opsi “try it out” pada setiap endpoint

# Algoritma Core Service
Tahapan yang dilakukan pada algoritma Perfume Recommendation  
1. Mendapatkan daftar notes parfum yang diinginkan pengguna
2. Apabila daftar notes parfum yang diinput pengguna tidak kosong, algoritma akan melakukan iterasi terhadap setiap data parfum yang tersedia dan mencocokkan notes parfum tersebut dengan yang diinginkan pengguna.
   Jika parfum memiliki setiap notes yang diinginkan pengguna, parfum tersebut akan dimasukkan kedalam array matching_perfume
3. Algoritma akan mengembalikan respon berisi daftar parfum yang cocok dengan keinginan pengguna berdasarkan array matching_perfume. Jika array matching_perfume kosong, algoritma akan menampilkan pesan yang sesuai

# API Endpoint  
Berikut API Endpoint yang terdapat pada program:
- Get Recommendation
    - Input: List berisi notes parfum yang bertipe string
    - Mengembalikan respon berupa daftar parfum yang cocok dengan semua input notes yang diinginkan pengguna
- Get Perfume Notes
    - Input: String nama parfum
    - Mengembalikan notes dari parfum yang diinput pengguna. Jika nama parfum tidak tersedia, maka program akan mengembalikan pesan yang sesuai.
- Delete Perfume
    - Input: String nama parfum
    - Menghapus data parfum yang diinput pengguna dari file json
- Update Perfume Notes
    - Input: String nama parfum yang hendak di-update notesnya dan string notes parfum yang akan ditambahkan ke notes yang sudah ada
    - Menambahkan notes parfum yang sudah ada dengan notes yang diinput pengguna
- Add New Perfume
    - Input: String nama parfum, string brand parfum, dan string berisi notes-notes parfum (notes parfum dipisahkan oleh ,)
    - Menambahkan entry parfum baru ke file json
