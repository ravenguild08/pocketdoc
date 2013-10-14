"""
  pocketdoc.py

  Peter Hung | peter-hung.com
  10/4-8 2013

  A cmdline interaction emulator of the first version of a bolus calculator
  designed by Dr. Lois Jovanovic et al., as described in Diabetes Care 1985, 8:172-76
"""

# input functions
def get_float(arg = ""):
  raw = raw_input(arg)
  while True:
    if raw != "":      
      try:
        return float(raw)
      except:
        pass      
    raw = raw_input("Invalid input! " + arg)
def get_nonzero_float(arg = ""):
  raw = 0
  while raw < 0.00001:
    raw = abs(get_float(arg))
  return raw
def get_string(arg = ""):
  raw = raw_input(arg)
  while raw == "":
    raw = raw_input("Invalid input! " + arg)
  return raw
def get_initial(arg = "", allowed = []):
  if len(allowed) == 0:
    return get_string(arg)[0].upper()
  uppers = map(lambda s: s[0].upper(), allowed)
  raw = get_string(arg)
  while raw[0].upper() not in uppers:
    print "Invalid input!",
    raw = get_string(arg)
  return raw[0].upper()

# pkd is a container for data and contains 5 functions that interact via cmdline
class Pkd(object):
  # asks user for demographic info and initializes relevant data
  def __init__(self):
    print "CSII PGM 9/83 EMULATOR"
    self.initials = get_string("your initials?: ").upper()
    self.gender_coeff = 12.7
    if get_initial("Male or female? (M/F) ", ['M', 'F']) == 'F':
      self.gender_coeff = 11.34
    self.adjustment = 1  
    self.weight = get_nonzero_float("Your weight, lbs = ? ")
    self.basalDay = get_nonzero_float("10am-4am basal = ? ")
    self.basalDawn = get_nonzero_float("4am-10am basal = ? ")
    self.avgBG = 0
    self.numTests = 0
    self.sumBG = 0
    self.runningCHO = 0
    self.runningCal = 0
    print "End"
    return

  # asks for time, blood glucose, info about meal, and prints a bolus value
  def bolus_plan(self):
    print "Mealtime Bolus Plan"
    isDay = self.is_day()
    bg = self.get_bg()

    if get_initial("Want basal check? (Y/N): ", ['Y', 'N']) == 'Y':
      tempBg = min(max(bg, 70), 250)
      factor = .833 + .00159 * tempBg
      if not isDay:
        self.basalDawn = round(self.basalDawn*factor, 1)
        print "4am-10am basal dose = ", self.basalDawn
      else: 
        self.basalDay = round(self.basalDay*factor, 1)
        print "10a-4am basal dose = ", self.basalDay

    carbs = get_float("Grams carbo.?: ")
    if carbs == 0:
      print "No meal. End"
      return
    calories = get_float("Calories this meal?: ")

    self.runningCHO += carbs
    self.runningCal += calories

    bg = min(max(bg, 70), 250)
    baseline_bolus = 0.005143 * bg - .48
    bolus = max(round(10*self.adjustment*carbs*self.sensitivity/self.gender_coeff +
                baseline_bolus*self.sensitivity*self.weight, 1), 0)
    print "Mealtime bolus = ", bolus
    # this section used to contain a failsafe for blood glucose of 0
    return bolus

  # asks for blood glucose and prepares for next meal.
  # ideally, can be integrated into mealtime bolus calculation
  def bolus_adj(self):
    print "Next Bolus Adj."
    bg = self.get_bg()
    bg = min(max(bg, 70), 250)
    self.adjustment = .2533 + bg / 187
    return self.adjustment

  # asks for time, blood glucose, and instructs on bolusing/eating depending on value
  def check(self):
    print "Between Meal Check"
    isDay = self.is_day()
    bg = self.get_bg()
    if bg < 70:
      print "Eat 10 gm. carbo. now!!"
      self.runningCHO += 10
      self.runningCal += 40
      return
    elif bg < 111:
      print "No bolus necessary"
      return
    factor = 0.001*min(bg, 250)-.081
    bolus = round(factor*self.sensitivity*self.weight, 1)
    print "Take bolus now!! = ", bolus
    return

  # helper function to ask for blood glucose
  def get_bg(self):
    bg = get_nonzero_float("Present blood sugar = ")
    self.numTests += 1
    self.sumBG += bg
    self.avgBG = round(self.sumBG/self.numTests)
    return bg

  # helper function to ask for time of day and set sensitivity
  def is_day(self):
    if get_initial("10am-4am? (Y/N): ", ['Y', 'N']) == 'N':
      self.sensitivity = .17
      return False
    else:
      self.sensitivity = .136
      return True

  # prints out user data and has options for reseting some values
  def summary(self):
    print self.initials + "'s adjustment plan"
    print "Ave.b.g. = ", self.avgBG, "Tests = ", self.numTests
    print "Running cho,gm. = ", int(self.runningCHO), "Running cal. = ", int(self.runningCal)
    if self.runningCHO != 0:
      print "Running %CHO =", round(400*self.runningCHO/self.runningCal)
      if get_initial("Reset CHO-Cal.? (Y/N): ", ['Y', 'N']) == 'Y':
        print 'Reset'
        self.runningCHO = 0
        self.runningCal = 0
    if self.avgBG == 0:
      print "End"
      return
    if get_initial("Reset b.adj. data? (Y/N): ", ['Y','N']) == "N":  
      print "End"
      return
    else:
      self.avgBG = 0
      self.numTests = 0
      self.sumBG = 0
      print "Reset-End"
      return

# generic loop that asks for user input
if __name__ == '__main__':
  pkd = Pkd()
  while True:
    menu = "1: Mealtime Bolus Plan\n2: Next Bolus Adjustment\n3: Between Meal Check\n4: Summary\n5: Reinitialize\n6: Quit\n"""
    choice = int(get_float(menu))
    if choice == 1:
      pkd.bolus_plan()
    elif choice == 2:
      pkd.bolus_adj()
    elif choice == 3:
      pkd.check()
    elif choice == 4:
      pkd.summary()
    elif choice == 5:
      pkd = Pkd()
    elif choice == 6:
      break
    else:
      print 'Try again. ',

  print 'Thank you, and goodbye!'