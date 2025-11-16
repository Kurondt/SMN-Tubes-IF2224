program test_full_tree;

konstanta
  maxVal = 100;
  piVal  = 3.14;
  greet  = 'tbfo';

tipe
  index = integer;
  realArray = larik[1..5] dari Real;
  letter = char;
  flag = boolean;

variabel
  x, y, z, sum, avg, count: integer;
  c: char;
  s: larik[1..10] dari char;
  arr: integer;
  done: boolean;

prosedur showMessage(msg: char);
mulai
  jika tidak done maka
    writeln('Program ', msg, ' seru sekali')
  selain_itu
    writeln('Selesai');
selesai;

fungsi add(a, b: integer): integer;
mulai
  add := a + b;
selesai;

mulai
  x := 22;
  y := 3;
  z := 2018;
  sum := x + y * (z bagi 10) - (x mod y);
  avg := (x + y + z) / 3.0;

  done := false;

  jika (sum >= maxVal) dan tidak done maka
    done := true
  selain_itu jika (sum < maxVal) atau (x <> y) maka
    done := false;

  jika (x <= y) maka
    done := false;

  while (x > 0) do
  mulai
    x := x - 1;
  selesai;

  arr[1] := 1.0;
  arr[2] := 2.5555;  
  arr[3] := 3.14;
  arr[4] := 4.0;
  arr[5] := 5.0;

  c := 'a';
  c := 'b';
  c := 'c';
  s := 'seru sekali';

  untuk count := 1 ke 5 lakukan
    sum := sum + count;

  untuk count := 5 turun_ke 1 lakukan
    avg := avg + arr[count];

  showMessage(greet);
  x := add(10, 20);

selesai.
