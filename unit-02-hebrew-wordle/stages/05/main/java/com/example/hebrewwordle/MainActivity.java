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

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "LIFECYCLE";
    private static final int ROWS = 6;          // ניסיונות
    private static final int COLS = 5;          // אותיות במילה

    private TextView[][] tiles;                 // [שורה][עמודה]
    private LinearLayout boardContainer;
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

        boardContainer = findViewById(R.id.boardContainer);
        buildBoard();
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
                tile.setBackground(ContextCompat.getDrawable(this, R.drawable.tile_empty));
                tile.setTextColor(ContextCompat.getColor(this, R.color.tile_text));

                tiles[row][col] = tile;
                rowLayout.addView(tile);
            }
            boardContainer.addView(rowLayout);
        }
    }

    /**
     * דרך 1: מאזין ב-XML. כל מקשי האותיות מצהירים android:onClick="onLetterKey"
     * (דרך הסגנון KeyButton), ולכן אנדרואיד מחפש כאן מתודה public בשם הזה
     * שמקבלת View אחד. הטקסט של הכפתור הוא האות עצמה.
     */
    public void onLetterKey(View view) {
        if (current.length() >= COLS) return;

        char letter = ((Button) view).getText().charAt(0);
        current.append(letter);
        int row = 0;                             // בינתיים: תמיד השורה הראשונה
        tiles[row][current.length() - 1].setText(String.valueOf(letter));
    }
}
