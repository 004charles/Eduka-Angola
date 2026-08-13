import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, TextInput, StatusBar, ActivityIndicator } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { chat } from '@/services/api';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
  green: '#159B5E',
};

export default function ChatScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ conversaId?: string; id?: string }>();
  const conversaId = params.conversaId || params.id || '1';

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const scrollViewRef = useRef<ScrollView>(null);

  useEffect(() => {
    loadMessages();
  }, [conversaId]);

  async function loadMessages() {
    try {
      setLoading(true);
      const data = await chat.getMensagens(conversaId);
      setMessages(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao carregar mensagens:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSend() {
    const text = input.trim();
    if (!text || sending) return;

    try {
      setSending(true);
      setInput('');
      const newMsg = await chat.enviarMensagem(conversaId, text);
      setMessages((prev) => [...prev, newMsg || {
        id: String(Date.now()),
        texto: text,
        text,
        hora: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
        time: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
        enviado: true,
        sent: true,
      }]);
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
      setInput(text);
    } finally {
      setSending(false);
    }
  }

  function formatTime(msg: any) {
    return msg.hora || msg.time || msg.timestamp || '';
  }

  function getMessageText(msg: any) {
    return msg.texto || msg.text || msg.conteudo || '';
  }

  function isSent(msg: any) {
    return msg.enviado || msg.sent || msg.remetente === 'eu';
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#fff" />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <MaterialCommunityIcons name="arrow-left" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>IP</Text>
        </View>
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>Suporte · IP Luanda</Text>
          <View style={styles.statusRow}>
            <View style={styles.onlineDot} />
            <Text style={styles.statusText}>Online agora</Text>
          </View>
        </View>
        <TouchableOpacity style={styles.callBtn}>
          <MaterialCommunityIcons name="phone" size={20} color={COLORS.purple} />
        </TouchableOpacity>
      </View>

      {/* Messages */}
      {loading ? (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <ActivityIndicator size="large" color={COLORS.purple} />
        </View>
      ) : (
        <ScrollView
          ref={scrollViewRef}
          style={styles.messages}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={() => scrollViewRef.current?.scrollToEnd({ animated: false })}
        >
          {messages.map((msg) => (
            <View
              key={msg.id}
              style={[styles.messageRow, isSent(msg) && styles.messageRowSent]}
            >
              <View style={[styles.bubble, isSent(msg) ? styles.bubbleSent : styles.bubbleReceived]}>
                <Text style={[styles.messageText, isSent(msg) && styles.messageTextSent]}>
                  {getMessageText(msg)}
                </Text>
                <Text style={[styles.messageTime, isSent(msg) && styles.messageTimeSent]}>
                  {formatTime(msg)}
                </Text>
              </View>
            </View>
          ))}
        </ScrollView>
      )}

      {/* Input Bar */}
      <View style={styles.inputBar}>
        <TouchableOpacity style={styles.attachBtn}>
          <MaterialCommunityIcons name="paperclip" size={22} color={COLORS.gray} />
        </TouchableOpacity>
        <TextInput
          style={styles.textInput}
          placeholder="Escrever mensagem…"
          placeholderTextColor={COLORS.gray}
          value={input}
          onChangeText={setInput}
          editable={!sending}
        />
        <TouchableOpacity
          style={[styles.sendBtn, sending && { opacity: 0.6 }]}
          activeOpacity={0.8}
          onPress={handleSend}
          disabled={sending || !input.trim()}
        >
          <MaterialCommunityIcons name="send" size={20} color="#fff" />
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bg,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
    gap: 10,
  },
  backBtn: {
    width: 38,
    height: 38,
    borderRadius: 10,
    backgroundColor: COLORS.bg,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatar: {
    width: 42,
    height: 42,
    borderRadius: 12,
    backgroundColor: COLORS.purple,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 14,
    fontWeight: '800',
    color: '#fff',
    fontFamily: 'System',
  },
  headerInfo: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    marginTop: 2,
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: COLORS.green,
  },
  statusText: {
    fontSize: 12,
    color: COLORS.green,
    fontFamily: 'System',
    fontWeight: '500',
  },
  callBtn: {
    width: 38,
    height: 38,
    borderRadius: 10,
    backgroundColor: COLORS.lightPurple,
    justifyContent: 'center',
    alignItems: 'center',
  },
  messages: {
    flex: 1,
  },
  messagesContent: {
    padding: 20,
    gap: 12,
  },
  messageRow: {
    flexDirection: 'row',
    justifyContent: 'flex-start',
  },
  messageRowSent: {
    justifyContent: 'flex-end',
  },
  bubble: {
    maxWidth: '78%',
    borderRadius: 16,
    padding: 14,
  },
  bubbleReceived: {
    backgroundColor: '#fff',
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  bubbleSent: {
    backgroundColor: COLORS.purple,
    borderBottomRightRadius: 4,
  },
  messageText: {
    fontSize: 14,
    fontWeight: '500',
    color: COLORS.dark,
    fontFamily: 'System',
    lineHeight: 20,
  },
  messageTextSent: {
    color: '#fff',
  },
  messageTime: {
    fontSize: 11,
    color: COLORS.gray,
    fontFamily: 'System',
    marginTop: 6,
  },
  messageTimeSent: {
    color: 'rgba(255,255,255,0.65)',
  },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    gap: 10,
  },
  attachBtn: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: COLORS.bg,
    justifyContent: 'center',
    alignItems: 'center',
  },
  textInput: {
    flex: 1,
    height: 44,
    backgroundColor: COLORS.bg,
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 14,
    fontWeight: '500',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  sendBtn: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: COLORS.purple,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
