package com.example.hebrewwordle.model;

/**
 * ניחוש אחד: המילה שהוקלדה והמצב של כל אות בה.
 * העצם הזה "קפוא" (immutable): אחרי שנוצר אי אפשר לשנות אותו - כך שורה שכבר נבדקה
 * לעולם לא משתנה בטעות.
 */
public class Guess {

    private final String word;
    private final LetterState[] states;

    public Guess(String word, LetterState[] states) {
        this.word = word;
        this.states = states;
    }

    public String getWord() {
        return word;
    }

    public LetterState getState(int index) {
        return states[index];
    }

    public LetterState[] getStates() {
        return states.clone();   // עותק, כדי שאף אחד בחוץ לא ישנה את המערך הפנימי
    }

    /** ניחוש "מנצח" הוא ניחוש שכל אותיותיו ירוקות. */
    public boolean isAllCorrect() {
        for (LetterState s : states) {
            if (s != LetterState.CORRECT) return false;
        }
        return true;
    }
}
