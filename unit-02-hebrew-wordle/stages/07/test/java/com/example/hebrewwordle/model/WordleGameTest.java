package com.example.hebrewwordle.model;

import static org.junit.Assert.*;
import static com.example.hebrewwordle.model.LetterState.*;

import org.junit.Test;

public class WordleGameTest {

    @Test
    public void allCorrectWhenGuessEqualsSecret() {
        LetterState[] r = WordleGame.evaluate("שולחן", "שולחן");
        assertArrayEquals(new LetterState[]{CORRECT, CORRECT, CORRECT, CORRECT, CORRECT}, r);
    }

    @Test
    public void letterInWrongPlaceIsPresent() {
        // ל נמצאת במילה הסודית במקום 3, בניחוש היא במקום 1
        LetterState[] r = WordleGame.evaluate("שולחן", "למדים");
        assertEquals(PRESENT, r[0]);
        assertEquals(ABSENT, r[1]);
    }

    @Test
    public void duplicateLetterIsCountedOnce() {
        // במילה הסודית יש ת אחת. בניחוש יש שתיים: רק אחת מקבלת צבע.
        LetterState[] r = WordleGame.evaluate("תלמיד", "תתתתת");
        assertEquals(CORRECT, r[0]);
        for (int i = 1; i < 5; i++) assertEquals(ABSENT, r[i]);
    }

    @Test
    public void greenWinsOverYellowForDuplicates() {
        // ב"ספינה" יש י אחת, באינדקס 2. בניחוש "ימיים" יש י באינדקסים 0, 2, 3.
        // ה-י היחידה של המילה הסודית נספרת בירוק באינדקס 2, ולכן שתי האחרות אפורות.
        LetterState[] r = WordleGame.evaluate("ספינה", "ימיים");
        assertEquals(ABSENT, r[0]);
        assertEquals(CORRECT, r[2]);
        assertEquals(ABSENT, r[3]);
    }

    @Test
    public void finalLettersMatchRegularLetters() {
        LetterState[] r = WordleGame.evaluate("שולחן", "שולחנ");
        assertEquals(CORRECT, r[4]);
    }

    @Test
    public void winOnSixthGuess() {
        WordleGame game = new WordleGame("שולחן");
        for (int i = 0; i < 5; i++) game.submit("תלמיד");
        assertFalse(game.isOver());
        game.submit("שולחן");
        assertTrue(game.isWon());
        assertTrue(game.isOver());
    }

    @Test
    public void loseAfterSixWrongGuesses() {
        WordleGame game = new WordleGame("שולחן");
        for (int i = 0; i < 6; i++) game.submit("תלמיד");
        assertTrue(game.isLost());
        assertFalse(game.isWon());
    }

    @Test(expected = IllegalArgumentException.class)
    public void shortGuessIsRejected() {
        new WordleGame("שולחן").submit("שול");
    }

    @Test(expected = IllegalStateException.class)
    public void noGuessAfterGameOver() {
        WordleGame game = new WordleGame("שולחן");
        game.submit("שולחן");
        game.submit("תלמיד");
    }
}
