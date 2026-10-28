package com.example.hebrewwordle;

import android.content.res.Resources;
import android.graphics.Typeface;
import android.os.Bundle;
import android.util.Log;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.hebrewwordle.model.Guess;
import com.example.hebrewwordle.model.LetterState;
import com.example.hebrewwordle.model.WordleGame;

import java.util.Random;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    private static final String TAG = "LIFECYCLE";
    private static final int ROWS = WordleGame.MAX_GUESSES;   // ניסיונות
    private static final int COLS = WordleGame.WORD_LENGTH;   // אותיות במילה

    private TextView[][] tiles;                 // [שורה][עמודה]
    private LinearLayout boardContainer;
    private TextView txtMessage;

    private WordleGame game;
    private final StringBuilder current = new StringBuilder();   // האותיות שהוקלדו בשורה הנוכחית

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
        Log.d(TAG, "onCreate - הפעילות נוצרת");

        txtMessage = findViewById(R.id.txtMessage);
        boardContainer = findViewById(R.id.boardContainer);
        buildBoard();
        wireButtons();
        startNewGame();
    }

    @Override
    protected void onStart() {
        super.onStart();
        Log.d(TAG, "onStart - המסך מוצג");
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.d(TAG, "onResume - אפשר ללחוץ על המסך");
    }

    @Override
    protected void onPause() {
        super.onPause();
        Log.d(TAG, "onPause - המסך מפסיק להגיב ללחיצות");
    }

    @Override
    protected void onStop() {
        super.onStop();
        Log.d(TAG, "onStop - המסך כבר לא מוצג");
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "onDestroy - הפעילות נהרסת");
    }

    /** בונה ROWS שורות של COLS אריחים. כל אריח הוא TextView עם רקע מ-drawable. */
    private void buildBoard() {
        Resources res = getResources();
        int size = res.getDimensionPixelSize(R.dimen.tile_size);
        int margin = res.getDimensionPixelSize(R.dimen.tile_margin);

        tiles = new TextView[ROWS][COLS];
        boardContainer.removeAllViews();

        for (int row = 0; row < ROWS; row++) {
            LinearLayout rowLayout = new LinearLayout(this);
            rowLayout.setOrientation(LinearLayout.HORIZONTAL);
            rowLayout.setGravity(Gravity.CENTER);

            for (int col = 0; col < COLS; col++) {
                TextView tile = new TextView(this);
                LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(size, size);
                lp.setMargins(margin, margin, margin, margin);
                tile.setLayoutParams(lp);
                tile.setGravity(Gravity.CENTER);
                tile.setTextSize(TypedValue.COMPLEX_UNIT_PX, res.getDimension(R.dimen.tile_text));
                tile.setTypeface(null, Typeface.BOLD);
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

    /**
     * דרך 1: מאזין ב-XML. כל מקשי האותיות מצהירים android:onClick="onLetterKey"
     * (דרך הסגנון KeyButton), ולכן אנדרואיד מחפש כאן מתודה public בשם הזה
     * שמקבלת View אחד. הטקסט של הכפתור הוא האות עצמה.
     */
    public void onLetterKey(View view) {
        if (game.isOver()) return;
        if (current.length() >= COLS) return;

        char letter = ((Button) view).getText().charAt(0);
        current.append(letter);
        int row = game.getGuessCount();          // השורה של הניחוש הנוכחי
        tiles[row][current.length() - 1].setText(String.valueOf(letter));
    }

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

    /**
     * דרך 3: מחלקה פנימית. למחלקה פנימית (לא static) יש גישה לכל השדות של הפעילות
     * - game, tiles, current - בלי להעביר אותם כפרמטרים.
     */
    private class CheckListener implements View.OnClickListener {
        @Override
        public void onClick(View view) {
            if (game.isOver()) return;
            if (current.length() < COLS) {
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

    /** מחבר את הכפתורים שלא מקבלים onClick ב-XML, כל אחד בדרך אחרת. */
    private void wireButtons() {
        findViewById(R.id.btnDelete).setOnClickListener(this);                 // דרך 2
        findViewById(R.id.btnCheck).setOnClickListener(new CheckListener());   // דרך 3
    }

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
    }

    /** מציג ניחוש שנבדק בשורה נתונה: אותיות וצבעי אריחים. */
    private void showGuess(int row, Guess guess) {
        String word = guess.getWord();
        for (int col = 0; col < COLS; col++) {
            tiles[row][col].setText(String.valueOf(word.charAt(col)));
            paintTile(tiles[row][col], guess.getState(col));
        }
    }

    private void updateMessage() {
        if (game.isWon()) {
            txtMessage.setText(getString(R.string.msg_win, game.getGuessCount()));
        } else if (game.isLost()) {
            txtMessage.setText(getString(R.string.msg_lose, game.getSecret()));
        } else {
            txtMessage.setText(getString(R.string.msg_guesses_left, ROWS - game.getGuessCount()));
        }
    }
}
