package com.example.ckpt1;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

import android.speech.RecognizerIntent;
import android.view.View;


import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.AuthFailureError;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.ProtocolException;
import java.net.URI;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Locale;
import java.net.URL;
import java.net.HttpURLConnection;
import java.util.Map;

public class MainActivity extends Activity {

    private TextView speech_result;
    private TextView esp_received;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        speech_result = (TextView) findViewById(R.id.speech_result);
        esp_received = (TextView) findViewById(R.id.esp_received);
    }

    public void getSpeechInput(View view) {

        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault());
        startActivityForResult(intent, 10);

    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        String speechResult = "";

        if(requestCode == 10 && resultCode == RESULT_OK){
            ArrayList<String> result = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
            speechResult = result.get(0).toString();
            speech_result.setText(speechResult);
        }

        RequestQueue queue = Volley.newRequestQueue(this);
        String url ="https://3cc52918b93a.ngrok.io";

        // Request a string response from the provided URL.
        String finalSpeechResult = speechResult;
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        // Display the first 500 characters of the response string
                        System.out.println(response.toString());
                        esp_received.setText(response.toString());

                    }
                }, new Response.ErrorListener() {
            @SuppressLint("SetTextI18n")
            @Override
            public void onErrorResponse(VolleyError error) {
                esp_received.setText("No Response from ESP!");
                System.out.println(error.toString());
            }
        }){
            @Override
            protected Map<String,String> getParams(){
                Map<String,String> params = new HashMap<String, String>();
                params.put("command","parameter send");
                return params;
            }

            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                Map<String,String> params = new HashMap<String, String>();
                System.out.println(finalSpeechResult);
                params.put("command", finalSpeechResult);
                return params;
            }
        };

        System.out.println("debug before");
        queue.add(stringRequest);
        System.out.println("debug after");

        super.onActivityResult(requestCode, resultCode, data);
    }
}


