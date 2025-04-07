import random
import os
import json # Example for loading adventure data
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import google.generativeai as genai

# --- PlayerCharacter and NPC Classes (from previous step) ---

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
        if not isinstance(stat_number, int) or not 2 <= stat_number <= 5:
            raise ValueError("Stat number must be an integer between 2 and 5.")

        self.name: str = name
        self.look: str = look
        self.role: str = role
        self.varulv_aspect: str = varulv_aspect
        self.stat_number: int = stat_number
        # Store the actual ability function/description later if needed
        self.special_ability_name: str = special_ability_name
        self.special_ability_used: bool = False
        self.conditions: list[str] = []

    def __str__(self) -> str:
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
        return (f"PlayerCharacter(name='{self.name}', role='{self.role}', "
                f"stat_number={self.stat_number}, "
                f"conditions={self.conditions}, "
                f"special_ability_used={self.special_ability_used})")

    def display_sheet(self) -> None:
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
        if self.is_incapacitated():
            print(f"{self.name} is already incapacitated and cannot take more conditions.")
            return False
        if condition_name in self.conditions:
            # Optionally allow stacking or just ignore
            # print(f"{self.name} already has condition: {condition_name}")
            # return False
            pass # Allow adding same condition name multiple times if desired

        self.conditions.append(condition_name.strip())
        print(f"Condition added to {self.name}: {condition_name.strip()}")
        if self.is_incapacitated():
            print(f"** {self.name} is now incapacitated! **")
        return True

    def remove_condition(self, condition_name: str) -> bool:
        condition_name = condition_name.strip()
        # Remove only the first instance if duplicates are allowed
        if condition_name in self.conditions:
            self.conditions.remove(condition_name)
            print(f"{self.name} recovers from: {condition_name}")
            return True
        else:
            print(f"{self.name} does not have condition: {condition_name}")
            return False

    def use_special_ability(self) -> bool:
        if self.special_ability_used:
            print(f"{self.name}'s special ability ({self.special_ability_name}) has already been used.")
            return False
        else:
            self.special_ability_used = True
            print(f"{self.name} uses their special ability: {self.special_ability_name}!")
            # Note: The *effect* of the ability still needs narrative handling
            return True

    def reset_special_ability(self) -> None:
        self.special_ability_used = False
        # print(f"{self.name}'s special ability ({self.special_ability_name}) has been reset.") # Optional print

    def reset_conditions(self) -> None:
        self.conditions = []
        # print(f"{self.name}'s conditions have been cleared.") # Optional print

    def is_incapacitated(self) -> bool:
        return len(self.conditions) >= self.MAX_CONDITIONS

    def get_stat_number(self) -> int:
        return self.stat_number

    def get_conditions(self) -> list[str]:
        return self.conditions.copy()

    def roll_check(self, approach: str) -> tuple[int, int, str]:
        if approach.upper() not in ['PRIMAL', 'TACTICAL']:
            raise ValueError("Approach must be 'PRIMAL' or 'TACTICAL'")

        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        results = sorted([d1, d2])
        stat_num = self.stat_number

        is_primal1 = results[0] < stat_num
        is_tactical1 = results[0] > stat_num
        is_critical1 = results[0] == stat_num

        is_primal2 = results[1] < stat_num
        is_tactical2 = results[1] > stat_num
        is_critical2 = results[1] == stat_num

        outcome = "Failure" # Default
        if is_critical1 or is_critical2:
            outcome = "Critical Success"
        elif (is_primal1 or is_primal2) and (is_tactical1 or is_tactical2):
             outcome = "Mixed Success"
        elif approach.upper() == 'PRIMAL' and (is_primal1 or is_primal2):
            outcome = "PRIMAL Success"
        elif approach.upper() == 'TACTICAL' and (is_tactical1 or is_tactical2):
             outcome = "TACTICAL Success"

        print(f"{self.name} rolls ({approach})... {d1}, {d2} vs {stat_num} -> {outcome}")
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
                 competence: int = 3,
                 status: str = "Active", # Added status field
                 notes: str = ""):
        self.name: str = name
        self.role_or_type: str = role_or_type
        self.description: str = description
        self.motivation: str = motivation
        self.competence: int = competence
        self.status: str = status # e.g., Active, Injured, Stunned, Captured, Dead
        self.notes: str = notes

    def __str__(self) -> str:
        return f"{self.name} ({self.role_or_type}) - Status: {self.status} | Motivation: {self.motivation}"

    def __repr__(self) -> str:
        return (f"NPC(name='{self.name}', role_or_type='{self.role_or_type}', "
                f"competence={self.competence}, status='{self.status}')")

    def display_profile(self) -> None:
        print("=" * 30)
        print(f"NPC: {self.name}")
        print(f"Role/Type: {self.role_or_type}")
        print(f"Description: {self.description}")
        print(f"Motivation: {self.motivation}")
        print(f"Competence Rating: {self.competence}")
        print(f"Status: {self.status}")
        if self.notes:
            print(f"Notes: {self.notes}")
        print("=" * 30)

    def get_competence(self) -> int:
        return self.competence

    def set_status(self, new_status: str):
        """Updates the NPC's status."""
        print(f"Updating status for {self.name} from '{self.status}' to '{new_status}'.")
        self.status = new_status

# --- Game Master Agent ---

class GameMasterAgent:
    """
    Agent responsible for handling narrative generation using Gemini.
    Relies on human GM input for mechanical state changes.
    """
    # Define available special abilities (name: description for prompt context)
    SPECIAL_ABILITIES_DESC = {
        "Primal Roar": "Unleash a terrifying howl to potentially stun or frighten enemies.",
        "Shadow Meld": "Blend perfectly with shadows or snow, becoming nearly invisible.",
        "Scent of the Prey/Foe": "Track someone unerringly or identify hidden dangers by smell.",
        "Iron Resolve": "Shake off mental effects or ignore penalties from one Condition.",
        "Saboteur's Touch": "Intuitively understand and manipulate machinery or explosives.",
        "Inspiring Howl/Word": "Rally an ally, letting them remove a Condition or gain an advantage.",
        "Rapid Healing": "Focus to remove one Condition from yourself.",
        "Pack Tactics": "Coordinate an attack or maneuver, granting an ally an advantage or allowing simultaneous action."
    }


    def __init__(self, game_state):
        """
        Initialize the GameMasterAgent with Gemini configuration.

        Args:
            game_state: Reference to the main Game object for context.
        """
        self.game_state = game_state # Access players, npcs, alert level etc.
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        # See https://ai.google.dev/models/gemini for model options
        # 'gemini-1.5-flash' is fast and capable for this usually
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.generation_config = genai.GenerationConfig(
            temperature=0.75, # Adjust for creativity vs consistency
            max_output_tokens=1000 # Limit response length
        )
        # Safety settings can be adjusted if needed, default is often fine
        # self.safety_settings = [...]


    def _build_prompt(self, player: PlayerCharacter, action_description: str, roll_info: tuple, approach: str, is_special_ability: bool) -> str:
        """Constructs the prompt for the Gemini LLM."""
        die1, die2, outcome = roll_info
        roll_summary = f"Roll ({approach}): {die1}, {die2} vs Stat {player.stat_number} -> {outcome}"

        # --- Context Gathering ---
        adventure_context = self.game_state.get_adventure_context() # Get current scene/objective
        player_statuses = "\n".join([f"- {p.name}: {len(p.conditions)} conditions ({', '.join(p.conditions)})" for p in self.game_state.players if not p.is_incapacitated()])
        npc_statuses = "\n".join([f"- {n.name} ({n.role_or_type}): Status {n.status}" for n in self.game_state.npcs if n.status != "Inactive/Dead"]) # Filter out inactive
        alert_level = self.game_state.alert_level

        # --- Base Prompt ---
        prompt = f"""
You are the Game Master for 'Varulv Vengeance', a gritty World War II TTRPG where players are werewolves in the Norwegian resistance fighting Nazis. Be descriptive, atmospheric, and maintain a tone of desperate struggle mixed with primal power.

**Game Rules Reminder:**
*   Players roll 2d6. PRIMAL actions succeed if a die is UNDER their Stat Number. TACTICAL actions succeed if a die is OVER their Stat Number.
*   Stat Number {player.stat_number}: Critical Success (roll = Stat Number), Mixed Success (one die PRIMAL success, one TACTICAL success), Failure (no success on chosen approach).
*   Conditions represent harm/stress. 4 Conditions = Incapacitated.
*   ALERT level tracks Nazi awareness. Higher ALERT means more guards, patrols, difficulty.

**Current Situation:**
*   Location/Objective: {adventure_context.get('current_scene', 'Unknown scene')} - {adventure_context.get('objective', 'Unknown objective')}
*   Current ALERT Level: {alert_level}
*   Active Player Characters:
{player_statuses if player_statuses else "    - None Active"}
*   Nearby NPCs:
{npc_statuses if npc_statuses else "    - None Visible"}

**Player Action:**
*   Character: {player.name} ({player.role} / {player.varulv_aspect})
*   Action Attempted: {action_description}
"""
        # --- Add Roll/Ability Info ---
        if is_special_ability:
             ability_desc = self.SPECIAL_ABILITIES_DESC.get(player.special_ability_name, "A unique power.")
             prompt += f"*   Used Special Ability: {player.special_ability_name} ({ability_desc})\n"
             # Note: Special abilities often auto-succeed or have specific roll mechanics
             # For simplicity here, we'll assume the GM tells the LLM the *intended* effect
             # based on the ability description, rather than rolling again unless the ability says so.
             # We pass the original roll that *triggered* the thought to use the ability, if applicable.
             prompt += f"*   (Related Roll, if any: {roll_summary})\n"
             prompt += f"*   Outcome Hint: Describe the powerful effect of the ability succeeding.\n"
        else:
            prompt += f"*   Roll Result: {roll_summary}\n"
            prompt += f"*   Outcome Hint: Describe the outcome based *directly* on the roll result category ({outcome}).\n"
            if outcome == "Critical Success":
                prompt += "      - Make it impressively effective AND grant the player a minor insight or advantage.\n"
            elif outcome == "Mixed Success":
                prompt += "      - They achieve their goal BUT with a complication, cost, or messy consequence (e.g., noise, damage, condition gained, ALERT increase hinted).\n"
            elif outcome == "Failure":
                prompt += "      - Describe how the action fails, potentially making things worse or revealing a new danger. Hint at a possible ALERT increase.\n"
            elif "Success" in outcome: # Primal or Tactical Success
                 prompt += "      - Describe them succeeding at their intended action clearly.\n"


        # --- Instruction ---
        prompt += f"""
**Your Task:**
Describe the scene and the immediate outcome of {player.name}'s action based on the context and the roll/ability result. Focus on sensory details (sight, sound, smell), tension, and the gritty WWII/werewolf theme.
**Crucially: DO NOT invent new game rules, conditions, or specific mechanical effects.** Stick to narrative description. Let the human GM handle mechanical updates after reading your response. Keep the response to 1-3 paragraphs.
"""
        return prompt.strip()


    def call_llm(self, prompt: str) -> str:
        """Calls the Gemini API with the given prompt."""
        try:
            # print("\n--- Sending Prompt to Gemini ---") # Debugging
            # print(prompt) # Debugging
            # print("--- End Prompt ---") # Debugging

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                # safety_settings=self.safety_settings # Optional
                )

            # Handle potential blocks or errors in response
            if not response.candidates:
                 # Check finish_reason if available, e.g., SAFETY
                 reason = response.prompt_feedback.block_reason if response.prompt_feedback else "Unknown"
                 print(f"Warning: LLM response blocked or empty. Reason: {reason}")
                 return f"[Narrative generation failed or was blocked. Reason: {reason}. GM describes the outcome manually.]"

            # Accessing text, handling potential errors if structure is unexpected
            if hasattr(response.candidates[0].content, 'parts') and response.candidates[0].content.parts:
                 return response.candidates[0].content.parts[0].text
            else:
                 # Fallback or different structure handling if needed
                 print("Warning: Unexpected LLM response structure.")
                 # Attempt to get text directly if possible
                 try:
                     return response.text
                 except AttributeError:
                     return "[Narrative generation failed due to unexpected response format. GM describes outcome.]"

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            # Provide traceback for debugging if needed:
            # import traceback
            # traceback.print_exc()
            return "[Error generating narrative. GM describes the outcome manually.]"

    def process_player_turn(self, player: PlayerCharacter, action_description: str):
        """Handles player action, rolls, LLM call, and narrative output."""
        print("-" * 20)
        print(f"Processing {player.name}'s turn...")

        is_special_ability = False
        # Simple check if player wants to use special ability
        if action_description.lower().startswith("special:") or \
           action_description.lower().startswith("ability:"):
            action_description = action_description.split(":", 1)[1].strip()
            if player.use_special_ability():
                is_special_ability = True
                # Special abilities often don't require a standard roll,
                # or have their own specific roll described in rules.
                # For simplicity, we'll pass a dummy roll result for context,
                # but the prompt emphasizes describing the ability's success.
                roll_info = (0, 0, "Special Ability Used")
                approach = "SPECIAL" # Indicate it's not a standard roll
                print(f"Using Special Ability: {player.special_ability_name}")
            else:
                print("Cannot use special ability now.")
                # Let the turn proceed as a normal action without the ability
                is_special_ability = False # Reset flag

        # If not using special ability, determine approach and roll
        if not is_special_ability:
            while True:
                approach = input(f"Is '{action_description}' primarily PRIMAL or TACTICAL? (P/T): ").upper()
                if approach == 'P':
                    approach = 'PRIMAL'
                    break
                elif approach == 'T':
                    approach = 'TACTICAL'
                    break
                else:
                    print("Invalid input. Please enter P or T.")

            roll_info = player.roll_check(approach) # Roll the dice

        # Build the prompt and call the LLM
        prompt = self._build_prompt(player, action_description, roll_info, approach, is_special_ability)
        narrative = self.call_llm(prompt)

        # Display the narrative
        print("\n--- GM Narrative ---")
        print(narrative)
        print("--- End Narrative ---\n")

        # --- MANUAL STATE UPDATE ---
        # This is where the human GM interprets the narrative and applies mechanics