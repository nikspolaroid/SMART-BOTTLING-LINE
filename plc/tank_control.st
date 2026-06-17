PROGRAM tank_control
  VAR
    tank_level    : REAL;
    inlet_valve   : BOOL;
    outlet_valve  : BOOL;
    alarm_overflow: BOOL;
    alarm_low     : BOOL;
  END_VAR

  (* Read tank level from simulation *)
  (* Level comes in as 0.0 to 100.0 percent *)

  (* Low level - open inlet valve *)
  IF tank_level <= 20.0 THEN
    inlet_valve := TRUE;
    alarm_low   := TRUE;
  END_IF;

  (* Tank full enough - close inlet *)
  IF tank_level >= 80.0 THEN
    inlet_valve  := FALSE;
    alarm_low    := FALSE;
    
  END_IF;

  (* Overflow alarm *)
  IF tank_level >= 90.0 THEN
    alarm_overflow := TRUE;
    outlet_valve   := TRUE;
  ELSE
    alarm_overflow := FALSE;
  END_IF;

END_PROGRAM
