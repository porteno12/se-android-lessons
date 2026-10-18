package com.example.hebrewwordle;

import android.content.res.Resources;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;

import com.example.hebrewwordle.model.Guess;
import com.example.hebrewwordle.model.LetterState;
import com.example.hebrewwordle.model.WordleGame;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * המסך היחיד של המשחק. הפעילות אחראית על שלושה דברים בלבד:
 * 1. לבנות את הלוח (30 אריחים) ולצבוע אותו לפי המצב של המשחק.
 * 2. לקבל לחיצות מהמקלדת ולהעביר אותן ל-WordleGame.
 * 3. לשמור ולשחזר את המצב כשהמסך מסתובב.
 * חוקי המשחק עצמם נמצאים ב-WordleGame, לא כאן.
 *
 * הפעילות "מממשת OnClickListener" - זו דרך 2 לטיפול באירועים (ראו onClick למטה).
 */
public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    //region step3-lifecycle
    private static final String TAG = "LIFECYCLE";
    //endregion

    //region step10-keys
    // מפתחות ל-Bundle של שמירת המצב
    private static final String KEY_SECRET = "secret";
    private static final String KEY_GUESSES = "guesses";
    private static final String KEY_CURRENT = "current";
    //endregion

    //region step5-fields
    private TextView[][] tiles;                 // [שורה][עמודה] - 6×5
    private LinearLayout boardContainer;
    private TextView txtMessage;
    //endregion

    //region step9-fields
    private WordleGame game;
    private final StringBuilder current = new StringBuilder();   // האותיות שהוקלדו בשורה הנוכחית
    private final Map<Character, Button> keyByLetter = new HashMap<>();
    //endregion

    //region step3-oncreate
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);      // תמיד קוראים ל-super קודם
        setContentView(R.layout.activity_main);
        Log.d(TAG, "onCreate - המסך נבנה. savedInstanceState=" + (savedInstanceState == null ? "null" : "יש מצב שמור"));

        txtMessage = findViewById(R.id.txtMessage);
        boardContainer = findViewById(R.id.boardContainer);
        buildBoard();                            // שלב 5
        collectKeyboardButtons();                // שלב 9
        wireButtons();                           // שלבים 8-9

        if (savedInstanceState == null) {
            startNewGame();                      // הפעלה רגילה
        } else {
            restoreGame(savedInstanceState);     // שלב 10: חזרה מסיבוב מסך
        }
    }
    //endregion

    //region step3-callbacks
    @Override
    protected void onStart() {
        super.onStart();
        Log.d(TAG, "onStart - המסך נהיה גלוי");
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.d(TAG, "onResume - המסך בחזית ומגיב ללחיצות");
    }

    @Override
    protected void onPause() {
        super.onPause();
        Log.d(TAG, "onPause - משהו כיסה אותי, אני מאבד פוקוס");
    }

    @Override
    protected void onStop() {
        super.onStop();
        Log.d(TAG, "onStop - אני כבר לא גלוי בכלל");
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "onDestroy - הפעילות נהרסת (סיבוב מסך או סגירה)");
    }
    //endregion

    //region step5-board
    /**
     * בונה 6 שורות של 5 אריחים בקוד. כל אריח הוא TextView רגיל עם רקע מ-drawable.
     * למה בקוד ולא ב-XML? כי 30 רכיבים זהים ב-XML הם 30 הזדמנויות לטעות העתקה,
     * ואילו לולאה כפולה היא 8 שורות.
     */
    private void buildBoard() {
        Resources res = getResources();
        int size = res.getDimensionPixelSize(R.dimen.tile_size);
        int margin = res.getDimensionPixelSize(R.dimen.tile_margin);

        tiles = new TextView[WordleGame.MAX_GUESSES][WordleGame.WORD_LENGTH];
        boardContainer.removeAllViews();

        for (int row = 0; row < WordleGame.MAX_GUESSES; row++) {
            LinearLayout rowLayout = new LinearLayout(this);
            rowLayout.setOrientation(LinearLayout.HORIZONTAL);
            rowLayout.setGravity(Gravity.CENTER);

            for (int col = 0; col < WordleGame.WORD_LENGTH; col++) {
                TextView tile = new TextView(this);
                LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(size, size);
                lp.setMargins(margin, margin, margin, margin);
                tile.setLayoutParams(lp);
                tile.setGravity(Gravity.CENTER);
                tile.setTextSize(android.util.TypedValue.COMPLEX_UNIT_PX, res.getDimension(R.dimen.tile_text));
                tile.setTypeface(null, android.graphics.Typeface.BOLD);
                paintTile(tile, LetterState.EMPTY);

                tiles[row][col] = tile;
                rowLayout.addView(tile);
            }
            boardContainer.addView(rowLayout);
        }
    }

    /** צובע אריח אחד לפי מצב. הצבעים עצמם יושבים ב-colors.xml וב-drawable. */
    private void paintTile(TextView tile, LetterState state) {
        int bg;
        int textColor = R.color.tile_text_light;
        switch (state) {
            case CORRECT: bg = R.drawable.tile_correct; break;
            case PRESENT: bg = R.drawable.tile_present; break;
            case ABSENT:  bg = R.drawable.tile_absent;  break;
            default:      bg = R.drawable.tile_empty;   textColor = R.color.tile_text; break;
        }
        tile.setBackground(ContextCompat.getDrawable(this, bg));
        tile.setTextColor(ContextCompat.getColor(this, textColor));
    }
    //endregion

    //region step7-letterkey
    /**
     * דרך 1: מאזין ב-XML. כל 27 מקשי האותיות מצהירים android:onClick="onLetterKey"
     * (דרך הסגנון KeyButton), ולכן אנדרואיד מחפש כאן מתודה public בשם הזה
     * שמקבלת View אחד. הטקסט של הכפתור הוא האות עצמה.
     */
    public void onLetterKey(View view) {
        if (game.isOver()) return;
        if (current.length() >= WordleGame.WORD_LENGTH) return;

        char letter = ((Button) view).getText().charAt(0);
        current.append(letter);
        int row = game.getGuessCount();
        tiles[row][current.length() - 1].setText(String.valueOf(letter));
    }
    //endregion

    //region step8-delete
    /**
     * דרך 2: הפעילות עצמה מממשת OnClickListener. כפתור "מחק" מקבל this כמאזין
     * (ראו wireButtons), ולכן הלחיצה מגיעה לכאן. כשיש כמה כפתורים עם אותו מאזין,
     * מבדילים ביניהם לפי view.getId().
     */
    @Override
    public void onClick(View view) {
        if (view.getId() == R.id.btnDelete) {
            if (game.isOver() || current.length() == 0) return;
            current.deleteCharAt(current.length() - 1);
            int row = game.getGuessCount();
            tiles[row][current.length()].setText("");
        }
    }
    //endregion

    //region step8-check
    /**
     * דרך 3: מחלקה פנימית. למחלקה פנימית (לא static) יש גישה לכל השדות של הפעילות
     * - game, tiles, current - בלי להעביר אותם כפרמטרים.
     */
    private class CheckListener implements View.OnClickListener {
        @Override
        public void onClick(View view) {
            if (game.isOver()) return;
            if (current.length() < WordleGame.WORD_LENGTH) {
                txtMessage.setText(R.string.msg_too_short);
                return;
            }
            Guess guess = game.submit(current.toString());
            int row = game.getGuessCount() - 1;
            showGuess(row, guess);
            current.setLength(0);
            updateMessage();
        }
    }
    //endregion

    //region step9-wire
    /** מחבר את שלושת הכפתורים שלא מקבלים onClick ב-XML, כל אחד בדרך אחרת. */
    private void wireButtons() {
        findViewById(R.id.btnDelete).setOnClickListener(this);                 // דרך 2
        findViewById(R.id.btnCheck).setOnClickListener(new CheckListener());   // דרך 3

        // דרך 4: מאזין אנונימי - מחלקה בלי שם שנכתבת במקום, מתאימה לקוד קצר של פעם אחת
        findViewById(R.id.btnNewGame).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startNewGame();
            }
        });
    }

    /** אוסף את כל מקשי האותיות למפה, כדי שנוכל לצבוע מקש לפי האות שלו. */
    private void collectKeyboardButtons() {
        keyByLetter.clear();
        LinearLayout keyboard = findViewById(R.id.keyboard);
        for (int r = 0; r < keyboard.getChildCount(); r++) {
            View rowView = keyboard.getChildAt(r);
            if (!(rowView instanceof LinearLayout)) continue;
            LinearLayout row = (LinearLayout) rowView;
            for (int i = 0; i < row.getChildCount(); i++) {
                View child = row.getChildAt(i);
                if (child instanceof Button && child.getId() == View.NO_ID) {
                    Button key = (Button) child;
                    keyByLetter.put(key.getText().charAt(0), key);
                }
            }
        }
    }
    //endregion

    //region step9-game
    private void startNewGame() {
        String[] words = getResources().getStringArray(R.array.words);
        String secret = words[new Random().nextInt(words.length)];
        game = new WordleGame(secret);
        current.setLength(0);
        clearBoard();
        txtMessage.setText(R.string.msg_start);
        Log.d(TAG, "משחק חדש. המילה הסודית: " + secret);   // רק לפיתוח - מוחקים לפני הגשה
    }

    private void clearBoard() {
        for (TextView[] row : tiles) {
            for (TextView tile : row) {
                tile.setText("");
                paintTile(tile, LetterState.EMPTY);
            }
        }
        for (Button key : keyByLetter.values()) {
            key.setBackgroundTintList(ContextCompat.getColorStateList(this, R.color.key_bg));
            key.setTextColor(ContextCompat.getColor(this, R.color.ink));
        }
    }

    /** מציג ניחוש שנבדק בשורה נתונה: אותיות, צבעי אריחים וצבעי מקשים. */
    private void showGuess(int row, Guess guess) {
        String word = guess.getWord();
        for (int col = 0; col < WordleGame.WORD_LENGTH; col++) {
            tiles[row][col].setText(String.valueOf(word.charAt(col)));
            paintTile(tiles[row][col], guess.getState(col));
            paintKey(word.charAt(col), guess.getState(col));
        }
    }

    /** מקש עולה בדרגה בלבד: אפור -> צהוב -> ירוק, אף פעם לא יורד. */
    private void paintKey(char letter, LetterState state) {
        Button key = keyByLetter.get(letter);
        if (key == null) return;
        LetterState old = (LetterState) key.getTag();
        if (old != null && old.ordinal() >= state.ordinal()) return;
        key.setTag(state);

        int color;
        switch (state) {
            case CORRECT: color = R.color.tile_correct; break;
            case PRESENT: color = R.color.tile_present; break;
            default:      color = R.color.tile_absent;  break;
        }
        key.setBackgroundTintList(ContextCompat.getColorStateList(this, color));
        key.setTextColor(ContextCompat.getColor(this, R.color.tile_text_light));
    }

    private void updateMessage() {
        if (game.isWon()) {
            txtMessage.setText(getString(R.string.msg_win, game.getGuessCount()));
        } else if (game.isLost()) {
            txtMessage.setText(getString(R.string.msg_lose, game.getSecret()));
        } else {
            txtMessage.setText(getString(R.string.msg_guesses_left,
                    WordleGame.MAX_GUESSES - game.getGuessCount()));
        }
    }
    //endregion

    //region step10-state
    /**
     * נקרא לפני שהפעילות נהרסת בגלל שינוי תצורה (סיבוב מסך, שינוי שפה...).
     * שומרים רק את המינימום שממנו אפשר לשחזר הכול: המילה הסודית, רשימת הניחושים
     * והאותיות שהוקלדו בשורה הנוכחית. את הצבעים לא שומרים - מחשבים אותם מחדש.
     */
    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putString(KEY_SECRET, game.getSecret());
        ArrayList<String> words = new ArrayList<>();
        for (Guess g : game.getGuesses()) words.add(g.getWord());
        outState.putStringArrayList(KEY_GUESSES, words);
        outState.putString(KEY_CURRENT, current.toString());
        Log.d(TAG, "onSaveInstanceState - נשמרו " + words.size() + " ניחושים");
    }

    /** בונה מחדש את המשחק מה-Bundle ומצייר את הלוח. */
    private void restoreGame(Bundle state) {
        String secret = state.getString(KEY_SECRET);
        List<String> words = state.getStringArrayList(KEY_GUESSES);
        String typed = state.getString(KEY_CURRENT, "");

        game = new WordleGame(secret);
        clearBoard();
        if (words != null) {
            for (int row = 0; row < words.size(); row++) {
                Guess guess = game.submit(words.get(row));   // הבדיקה מחדש נותנת שוב את הצבעים
                showGuess(row, guess);
            }
        }
        current.setLength(0);
        current.append(typed);
        int row = game.getGuessCount();
        for (int col = 0; col < typed.length() && row < WordleGame.MAX_GUESSES; col++) {
            tiles[row][col].setText(String.valueOf(typed.charAt(col)));
        }
        updateMessage();
        Log.d(TAG, "restoreGame - שוחזרו " + (words == null ? 0 : words.size()) + " ניחושים");
    }
    //endregion
}
