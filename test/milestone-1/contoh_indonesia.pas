program HitungStatistik;

konstanta
  BATAS_MAKS = 10;

tipe
  indeks = integer;
  daftar_nilai = larik[1..10] dari integer;
  koordinat = rekaman
    x: Real;
    y: Real;
    valid: boolean;
  selesai;

prosedur tulis_garis(panjang: integer);
variabel idx: integer;
mulai
  idx := 1;
  selama idx <= panjang lakukan
  mulai
    write('-');
    idx := idx + 1;
  selesai;
  writeln;
selesai;

fungsi faktorial(x: integer): integer;
variabel sementara: integer;
mulai
  jika x <= 1 maka
    faktorial := 1
  selain_itu
  mulai
    sementara := x * faktorial(x - 1);
    faktorial := sementara;
  selesai;
selesai;

variabel
  n, i: integer;
  angka: daftar_nilai;
  jumlah: integer;
  rata: real;
  posisi: koordinat;
  flag: boolean;
  perintah: char;
  hasil_bagi, sisa: integer;

mulai
  writeln('Masukkan jumlah data (maks 10):');
  readln(n);

  jika n <= 0 maka
  mulai
    writeln('Nilai n minimal 1, diset ke 1');
    n := 1;
  selesai
  selain_itu
  jika n > BATAS_MAKS maka
  mulai
    writeln('Jumlah melewati batas, diset ke 10');
    n := BATAS_MAKS;
  selesai;

  jumlah := 0;
  untuk i := 1 ke n lakukan
  mulai
    write('Data ke-', i, ': ');
    readln(angka[i]);
    jumlah := jumlah + angka[i];
  selesai;

  untuk i := n turun_ke 1 lakukan
  mulai
    writeln('Nilai mundur[', i, '] = ', angka[i]);
  selesai;

  rata := jumlah / n;
  hasil_bagi := jumlah bagi n;
  sisa := jumlah mod n;
  writeln('Rata-rata = ', rata:0:2, ', bagi bulat = ', hasil_bagi, ', sisa = ', sisa);

  flag := (n > 0) dan tidak ((jumlah = 0) atau (angka[1] = 0));
  jika flag maka
    writeln('Ada data valid')
  selain_itu
    writeln('Data tidak valid');

  posisi.x := angka[1];
  posisi.y := angka[n];
  posisi.valid := true;

  ulangi
  mulai
    write('Masukkan Y untuk cetak faktorial: ');
    readln(perintah);
  selesai
  sampai (perintah = 'Y');

  writeln('Faktorial ', n, ' = ', faktorial(n));

  kasus n dari
    0: writeln('Kasus nol');
    1, 2, 3: writeln('Kasus kecil');
  selain_itu
    writeln('Kasus besar');
  selesai;

  selama posisi.valid lakukan
  mulai
    tulis_garis(10);
    writeln('Koordinat X = ', posisi.x:0:0, ', Y = ', posisi.y:0:0);
    posisi.valid := false;
  selesai;

selesai.
