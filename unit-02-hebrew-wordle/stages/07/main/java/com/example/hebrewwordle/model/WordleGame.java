package com.example.hebrewwordle.model;

import java.util.ArrayList;
import java.util.List;

/**
 * חוקי המשחק, ב-Java טהור. המחלקה הזאת לא יודעת שקיים אנדרואיד:
 * אין כאן TextView, אין Button, אין צבעים. בגלל זה אפשר לבדוק אותה ב-JUnit
 * על המחשב, בלי אמולטור.
 */
public class WordleGame {

    public static final int WORD_LENGTH = 5;
    public static final int MAX_GUESSES = 6;

    private final String secret;
    private final List<Guess> guesses = new ArrayList<>();

    public WordleGame(String secret) {
        if (secret == null || secret.length() != WORD_LENGTH) {
            throw new IllegalArgumentException("המילה הסודית חייבת להיות בת " + WORD_LENGTH + " אותיות");
        }
        this.secret = secret;
    }

    /**
     * בודק ניחוש ומוסיף אותו לרשימה.
     * @throws IllegalArgumentException אם אורך המילה שגוי
     * @throws IllegalStateException אם המשחק כבר נגמר
     */
    public Guess submit(String word) {
        if (isOver()) {
            throw new IllegalStateException("המשחק נגמר");
        }
        if (word == null || word.length() != WORD_LENGTH) {
            throw new IllegalArgumentException("הניחוש חייב להיות בן " + WORD_LENGTH + " אותיות");
        }
        Guess guess = new Guess(word, evaluate(secret, word));
        guesses.add(guess);
        return guess;
    }

    /**
     * לב המשחק: משווה ניחוש למילה הסודית ומחזיר מצב לכל אות.
     * שני מעברים: קודם מסמנים ירוקים, ורק אחר כך צהובים - אחרת אות כפולה
     * בניחוש הייתה "גונבת" צהוב שלא מגיע לה.
     */
    public static LetterState[] evaluate(String secret, String word) {
        LetterState[] result = new LetterState[WORD_LENGTH];
        char[] s = normalize(secret).toCharArray();
        char[] g = normalize(word).toCharArray();
        boolean[] usedInSecret = new boolean[WORD_LENGTH];

        // מעבר 1: ירוקים
        for (int i = 0; i < WORD_LENGTH; i++) {
            if (g[i] == s[i]) {
                result[i] = LetterState.CORRECT;
                usedInSecret[i] = true;
            }
        }
        // מעבר 2: צהובים ואפורים
        for (int i = 0; i < WORD_LENGTH; i++) {
            if (result[i] != null) continue;          // כבר ירוק
            result[i] = LetterState.ABSENT;
            for (int j = 0; j < WORD_LENGTH; j++) {
                if (!usedInSecret[j] && g[i] == s[j]) {
                    result[i] = LetterState.PRESENT;
                    usedInSecret[j] = true;         // כל אות במילה הסודית "משלמת" פעם אחת
                    break;
                }
            }
        }
        return result;
    }

    /**
     * אותיות סופיות נחשבות כאות הרגילה: מי שהקליד "מ" במקום "ם" עדיין צודק לגבי האות.
     */
    public static String normalize(String word) {
        return word.replace('ך', 'כ')
                   .replace('ם', 'מ')
                   .replace('ן', 'נ')
                   .replace('ף', 'פ')
                   .replace('ץ', 'צ');
    }

    public boolean isWon() {
        return !guesses.isEmpty() && guesses.get(guesses.size() - 1).isAllCorrect();
    }

    public boolean isLost() {
        return !isWon() && guesses.size() >= MAX_GUESSES;
    }

    public boolean isOver() {
        return isWon() || isLost();
    }

    public String getSecret() {
        return secret;
    }

    public List<Guess> getGuesses() {
        return new ArrayList<>(guesses);
    }

    public int getGuessCount() {
        return guesses.size();
    }
}
