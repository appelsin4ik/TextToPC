package com.example.textbridge

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

private const val SERVER_IP = "192.168.0.101" // <- сюда впиши IP своего ПК
private const val SERVER_PORT = 5000

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            TextBridgeTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    TextBridgeScreen()
                }
            }
        }
    }
}

@Composable
fun TextBridgeScreen() {
    var text by remember { mutableStateOf("") }
    var isSending by remember { mutableStateOf(false) }
    var status by remember { mutableStateOf("Ready") }
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF0B1220),
                        Color(0xFF0F172A),
                        Color(0xFF111827)
                    )
                )
            )
            .statusBarsPadding()
            .navigationBarsPadding()
    ) {
        SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(16.dp)
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(20.dp),
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = "TextBridge",
                style = MaterialTheme.typography.headlineMedium,
                color = Color.White,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Write on Android — get it instantly on your PC clipboard.",
                color = Color(0xFF94A3B8),
                style = MaterialTheme.typography.bodyMedium
            )

            Spacer(modifier = Modifier.height(18.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF111827)
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 12.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(18.dp)
                ) {
                    Text(
                        text = "Connected PC",
                        color = Color(0xFFE5E7EB),
                        fontWeight = FontWeight.SemiBold
                    )

                    Spacer(modifier = Modifier.height(4.dp))

                    Text(
                        text = "$SERVER_IP:$SERVER_PORT",
                        color = Color(0xFF60A5FA)
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    OutlinedTextField(
                        value = text,
                        onValueChange = { text = it },
                        label = { Text("Type your text") },
                        placeholder = { Text("Например: ссылка, заметка, код, команда...") },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(220.dp),
                        shape = RoundedCornerShape(18.dp)
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Button(
                        onClick = {
                            scope.launch {
                                if (text.isBlank()) {
                                    snackbarHostState.showSnackbar("Текст пустой")
                                    return@launch
                                }

                                isSending = true
                                status = "Sending..."

                                val result = sendTextToPc(text)

                                status = result
                                isSending = false

                                if (result == "Sent successfully") {
                                    snackbarHostState.showSnackbar("Отправлено")
                                    text = ""
                                } else {
                                    snackbarHostState.showSnackbar(result)
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = !isSending,
                        shape = RoundedCornerShape(16.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF2563EB)
                        )
                    ) {
                        Text(
                            text = if (isSending) "Sending..." else "Send to PC",
                            color = Color.White
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Text(
                        text = "Status: $status",
                        color = Color(0xFFCBD5E1)
                    )
                }
            }
        }
    }
}

suspend fun sendTextToPc(text: String): String {
    if (text.isBlank()) return "Text is empty"

    return withContext(Dispatchers.IO) {
        try {
            val url = URL("http://$SERVER_IP:$SERVER_PORT/text")
            val connection = (url.openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = 5000
                readTimeout = 5000
                doOutput = true
                setRequestProperty("Content-Type", "application/json")
            }

            val body = JSONObject().apply {
                put("text", text)
            }.toString()

            OutputStreamWriter(connection.outputStream).use { writer ->
                writer.write(body)
                writer.flush()
            }

            val code = connection.responseCode
            if (code in 200..299) {
                "Sent successfully"
            } else {
                "Server error: $code"
            }
        } catch (e: Exception) {
            "Error: ${e.message}"
        }
    }
}

@Composable
fun TextBridgeTheme(content: @Composable () -> Unit) {
    val colors = darkColorScheme(
        primary = Color(0xFF2563EB),
        background = Color(0xFF0B1220),
        surface = Color(0xFF111827)
    )

    MaterialTheme(
        colorScheme = colors,
        content = content
    )
}