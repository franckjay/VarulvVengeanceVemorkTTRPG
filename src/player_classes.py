import random

class PlayerCharacter:
    """
    Represents a Player Character (Varulv) in the TTRPG.
    """
    MAX_CONDITIONS = 4 # Number of conditions before being incapacitated

    def __init__(self,
                 name: str,
                 look: str,
                 role: str,
                 varulv_aspect: str,
                 stat_number: int,
                 special_ability_name: str):
        """
        Initializes a Player Character.

        Args:
            name: The character's name.
            look: A brief description of the character's appearance.
            role: The character's primary function (e.g., Saboteur, Scout).
            varulv_aspect: The character's specific werewolf trait (e.g., Hulking Beast).
            stat_number: The character's core stat number (2, 3, 4, or 5).
            special_ability_name: The name of the chosen special ability.
        """
        if not isinstance(stat_number, int) or not 2 <= stat_number <= 5:
            raise ValueError("Stat number must be an integer between 2 and 5.")

        self.name: str = name
        self.look: str = look
        self.role: str = role
        self.varulv_aspect: str = varulv_aspect
        self.stat_number: int = stat_number
        self.special_ability_name: str = special_ability_name
        self.special_ability_used: bool = False
        self.conditions: list[str] = []

    def __str__(self) -> str:
        """Provides a user-friendly string representation."""
        status = "OK"
        if self.is_incapacitated():
            status = "Incapacitated"
        elif self.conditions:
            status = f"Suffering ({len(self.conditions)})"

        ability_status = "Available" if not self.special_ability_used else "Used"

        return (f"{self.name} ({self.role} / {self.varulv_aspect}) "
                f"| Stat: {self.stat_number} | Status: {status} "
                f"| Ability: {self.special_ability_name} ({ability_status})")

    def __repr__(self) -> str:
        """Provides an unambiguous string representation for debugging."""
        return (f"PlayerCharacter(name='{self.name}', role='{self.role}', "
                f"stat_number={self.stat_number}, "
                f"conditions={self.conditions}, "
                f"special_ability_used={self.special_ability_used})")

    def display_sheet(self) -> None:
        """Prints a formatted character sheet to the console."""
        print("-" * 30)
        print(f"Name: {self.name}")
        print(f"Look: {self.look}")
        print(f"Role: {self.role}")
        print(f"Varulv Aspect: {self.varulv_aspect}")
        print("-" * 30)
        print(f"STAT NUMBER: {self.stat_number}")
        print(f"  (Roll UNDER for PRIMAL, OVER for TACTICAL)")
        print("-" * 30)
        print(f"Special Ability: {self.special_ability_name}")
        print(f"  Used this adventure: {'Yes' if self.special_ability_used else 'No'}")
        print("-" * 30)
        print("Conditions:")
        if self.conditions:
            for i, cond in enumerate(self.conditions):
                print(f"  {i+1}. {cond}")
        else:
            print("  None")
        if self.is_incapacitated():
            print("\n  ** INCAPACITATED **")
        print("-" * 30)

    def add_condition(self, condition_name: str) -> bool:
        """
        Adds a condition to the character.

        Args:
            condition_name: The descriptive name of the condition (e.g., "Injured Arm").

        Returns:
            True if the condition was added, False if they are already incapacitated
            or already have this specific condition.
        """
        if self.is_incapacitated():
            print(f"{self.name} is already incapacitated and cannot take more conditions.")
            return False
        if condition_name in self.conditions:
            print(f"{self.name} already has condition: {condition_name}")
            return False

        self.conditions.append(condition_name)
        print(f"{self.name} gains condition: {condition_name}")
        if self.is_incapacitated():
            print(f"** {self.name} is now incapacitated! **")
        return True

    def remove_condition(self, condition_name: str) -> bool:
        """
        Removes a condition from the character.

        Args:
            condition_name: The name of the condition to remove.

        Returns:
            True if the condition was removed, False if it wasn't found.
        """
        if condition_name in self.conditions:
            self.conditions.remove(condition_name)
            print(f"{self.name} recovers from: {condition_name}")
            return True
        else:
            print(f"{self.name} does not have condition: {condition_name}")
            return False

    def use_special_ability(self) -> bool:
        """
        Marks the special ability as used for the current adventure.

        Returns:
            True if the ability was marked as used, False if it was already used.
        """
        if self.special_ability_used:
            print(f"{self.name}'s special ability ({self.special_ability_name}) has already been used.")
            return False
        else:
            self.special_ability_used = True
            print(f"{self.name} uses their special ability: {self.special_ability_name}!")
            return True

    def reset_special_ability(self) -> None:
        """Resets the special ability usage, typically between adventures."""
        self.special_ability_used = False
        print(f"{self.name}'s special ability ({self.special_ability_name}) has been reset.")

    def reset_conditions(self) -> None:
        """Removes all conditions, typically between adventures or after significant rest."""
        self.conditions = []
        print(f"{self.name}'s conditions have been cleared.")


    def is_incapacitated(self) -> bool:
        """Checks if the character has reached the maximum number of conditions."""
        return len(self.conditions) >= self.MAX_CONDITIONS

    def get_stat_number(self) -> int:
        """Returns the character's core stat number."""
        return self.stat_number

    def get_conditions(self) -> list[str]:
        """Returns the list of current conditions."""
        return self.conditions.copy() # Return a copy to prevent external modification

    def roll_check(self, approach: str) -> tuple[int, int, str]:
        """
        Performs a PRIMAL or TACTICAL roll and determines the outcome type.

        Args:
            approach: Either 'PRIMAL' or 'TACTICAL'.

        Returns:
            A tuple containing: (die1_result, die2_result, outcome_type)
            outcome_type can be: 'Critical Success', 'PRIMAL Success',
                                 'TACTICAL Success', 'Mixed Success', 'Failure'
        """
        if approach.upper() not in ['PRIMAL', 'TACTICAL']:
            raise ValueError("Approach must be 'PRIMAL' or 'TACTICAL'")

        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        results = sorted([d1, d2]) # Makes checking easier

        is_primal1 = results[0] < self.stat_number
        is_tactical1 = results[0] > self.stat_number
        is_critical1 = results[0] == self.stat_number

        is_primal2 = results[1] < self.stat_number
        is_tactical2 = results[1] > self.stat_number
        is_critical2 = results[1] == self.stat_number

        # Check for Critical Success first
        if is_critical1 or is_critical2:
            outcome = "Critical Success"
        # Check for Mixed Success
        elif (is_primal1 or is_primal2) and (is_tactical1 or is_tactical2):
             outcome = "Mixed Success"
        # Check for specific approach success
        elif approach.upper() == 'PRIMAL':
            if is_primal1 or is_primal2:
                outcome = "PRIMAL Success"
            else:
                outcome = "Failure"
        elif approach.upper() == 'TACTICAL':
             if is_tactical1 or is_tactical2:
                 outcome = "TACTICAL Success"
             else:
                 outcome = "Failure"
        else: # Should not happen due to initial check, but good failsafe
             outcome = "Failure"

        print(f"{self.name} rolls ({approach})... {d1}, {d2} vs {self.stat_number} -> {outcome}")
        return d1, d2, outcome


class NPC:
    """
    Represents a generic Non-Player Character.
    """
    def __init__(self,
                 name: str,
                 role_or_type: str,
                 description: str,
                 motivation: str,
                 competence: int = 3, # General capability rating (e.g., 1-6)
                 notes: str = ""):
        """
        Initializes a Non-Player Character.

        Args:
            name: The NPC's name or designation (e.g., "Guard Captain").
            role_or_type: Their function or type (e.g., "Gestapo Officer", "Civilian").
            description: A brief visual or behavioral description.
            motivation: What drives this NPC? (e.g., "Fear", "Duty", "Greed").
            competence: A general rating of their capability (default 3).
            notes: Any additional relevant information for the GM.
        """
        self.name: str = name
        self.role_or_type: str = role_or_type
        self.description: str = description
        self.motivation: str = motivation
        self.competence: int = competence
        self.notes: str = notes

    def __str__(self) -> str:
        """Provides a user-friendly string representation."""
        return f"{self.name} ({self.role_or_type}) - Motivation: {self.motivation}"

    def __repr__(self) -> str:
        """Provides an unambiguous string representation for debugging."""
        return (f"NPC(name='{self.name}', role_or_type='{self.role_or_type}', "
                f"competence={self.competence})")

    def display_profile(self) -> None:
        """Prints a formatted NPC profile to the console."""
        print("=" * 30)
        print(f"NPC: {self.name}")
        print(f"Role/Type: {self.role_or_type}")
        print(f"Description: {self.description}")
        print(f"Motivation: {self.motivation}")
        print(f"Competence Rating: {self.competence}")
        if self.notes:
            print(f"Notes: {self.notes}")
        print("=" * 30)

    def get_competence(self) -> int:
        """Returns the NPC's competence rating."""
        return self.competence