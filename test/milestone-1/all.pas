program test_full_tokens;

const
  maxVal = 100;
  piVal  = 3.14;
  greet  = 'tbfo';

type
  index = integer;
  realArray = array[1..5] of real;
  letter = char;
  flag = boolean;

var
  x, y, z, sum, avg, count: integer;
  c: char;
  s: string;
  arr: realArray;
  done: boolean;

procedure showMessage(msg: string);
begin
  if not done then
    writeln('Program ', msg, ' seru sekali')
  else
    writeln('Selesai');
end;

function add(a, b: integer): integer;
begin
  add := a + b;
end;

begin
  x := 22;
  y := 3;
  z := 2018;
  sum := x + y * (z div 10) - (x mod y);
  avg := (x + y + z) / 3.0;

  done := false;

  if (sum >= maxVal) and not done then
    done := true
  else if (sum < maxVal) or (x <> y) then
    done := false;

  if (x <= y) then
    done := false;

  while (x > 0) do
  begin
    x := x - 1;
  end;

  arr[1] := 1.0;
  arr[2] := 2.5555;  
  arr[3] := 3.14;
  arr[4] := 4.0;
  arr[5] := 5.0;

  c := 'a';
  c := 'b';
  c := 'c';
  s := 'seru sekali';

  for count := 1 to 5 do
    sum := sum + count;

  for count := 5 downto 1 do
    avg := avg + arr[count];

  showMessage(greet);
  x := add(10, 20);

end.
