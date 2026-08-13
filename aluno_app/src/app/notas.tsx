import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, TextInput, StatusBar } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
};

const NOTES = [
  {
    id: '1',
    timestamp: '04:12',
    text: 'Flexbox alinha itens numa dimensão. Usar justify-content para o eixo principal.',
  },
  {
    id: '2',
    timestamp: '07:45',
    text: 'Grid é bidimensional — rever grid-template-columns no exercício.',
  },
];

export default function NotasScreen() {
  const router = useRouter();
  const [newNote, setNewNote] = useState('');

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <MaterialCommunityIcons name="arrow-left" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>As minhas notas</Text>
          <Text style={styles.headerSubtitle}>Programação Web · Aula 4</Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      {/* Notes List */}
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {NOTES.map((note) => (
          <View key={note.id} style={styles.noteCard}>
            <View style={styles.noteHeader}>
              <View style={styles.timestampBadge}>
                <MaterialCommunityIcons name="clock-outline" size={14} color={COLORS.purple} />
                <Text style={styles.timestampText}>{note.timestamp}</Text>
              </View>
              <TouchableOpacity>
                <MaterialCommunityIcons name="dots-vertical" size={20} color={COLORS.gray} />
              </TouchableOpacity>
            </View>
            <Text style={styles.noteText}>{note.text}</Text>
          </View>
        ))}
        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Bottom Input */}
      <View style={styles.inputBar}>
        <TextInput
          style={styles.textInput}
          placeholder="Adicionar nota…"
          placeholderTextColor={COLORS.gray}
          value={newNote}
          onChangeText={setNewNote}
        />
        <TouchableOpacity style={styles.addBtn} activeOpacity={0.8}>
          <MaterialCommunityIcons name="plus" size={24} color="#fff" />
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
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  headerCenter: {
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  headerSubtitle: {
    fontSize: 13,
    color: COLORS.gray,
    fontFamily: 'System',
    marginTop: 2,
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 20,
  },
  noteCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 12,
  },
  noteHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  timestampBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: COLORS.lightPurple,
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 20,
  },
  timestampText: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.purple,
    fontFamily: 'System',
  },
  noteText: {
    fontSize: 14,
    fontWeight: '500',
    color: COLORS.dark,
    fontFamily: 'System',
    lineHeight: 22,
  },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    gap: 10,
  },
  textInput: {
    flex: 1,
    height: 48,
    backgroundColor: COLORS.bg,
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 14,
    fontWeight: '500',
    color: COLORS.dark,
    fontFamily: 'System',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  addBtn: {
    width: 48,
    height: 48,
    borderRadius: 12,
    backgroundColor: COLORS.purple,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
