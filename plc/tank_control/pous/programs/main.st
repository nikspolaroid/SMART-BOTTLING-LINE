PROGRAM main
  VAR
    tank_level : REAL := 0.0;
    inlet_valve : BOOL := FALSE;
    outlet_valve : BOOL := FALSE;
    alarm_overflow : BOOL := FALSE;
    alarm_low : BOOL := FALSE;
  END_VAR

IF tank_level <= 20.0 THEN
  inlet_valve := TRUE;
  alarm_low := TRUE;
END_IF;

IF tank_level >= 80.0 THEN
  inlet_valve := FALSE;
  alarm_low := FALSE;
END_IF;

IF tank_level >= 90.0 THEN
  alarm_overflow := TRUE;
  outlet_valve := TRUE;
ELSE
  alarm_overflow := FALSE;
END_IF;

END_PROGRAM