program Calc;
var
  a, b, c: integer;
begin
  a := 7 + 3 * 2 -4 / 2 - 3 + (-1);
  b := a div 3;
  c := a mod 4;
  writeln('a = ', a);
  writeln('b = ', b);
  writeln('c = ', c);
end.
