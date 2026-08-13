import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { candidaturas, parcerias, cursos } from '@/services/api';
import * as ImagePicker from 'expo-image-picker';

export default function CandidaturaScreen() {
  const router = useRouter();
  const { parceria: parceriaId } = useLocalSearchParams();
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [partner, setPartner] = useState<any>(null);
  const [courseList, setCourseList] = useState<any[]>([]);

  const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [telefone, setTelefone] = useState('');
  const [bi, setBi] = useState('');
  const [docUri, setDocUri] = useState<string | null>(null);
  const [comprovativoUri, setComprovativoUri] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [parceriaId]);

  async function loadData() {
    try {
      setLoading(true);
      const coursesData = await cursos.list();
      setCourseList(Array.isArray(coursesData) ? coursesData : (coursesData as any).results || []);
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
    } finally {
      setLoading(false);
    }
  }

  async function pickDocument(setUri: (uri: string | null) => void) {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: false,
      quality: 0.8,
    });
    if (!result.canceled && result.assets[0]) {
      setUri(result.assets[0].uri);
    }
  }

  async function handleSubmit() {
    if (!selectedCourse) {
      Alert.alert('Erro', 'Selecione um curso.');
      return;
    }
    if (!nome.trim() || !email.trim() || !telefone.trim()) {
      Alert.alert('Erro', 'Preencha todos os campos obrigatórios.');
      return;
    }

    try {
      setSubmitting(true);
      await candidaturas.create({
        parceria: Number(parceriaId),
        curso: selectedCourse,
        nome_completo: nome.trim(),
        email: email.trim(),
        telefone: telefone.trim(),
        bi: bi.trim(),
      });
      Alert.alert('Sucesso', 'Candidatura submetida com sucesso!', [
        { text: 'OK', onPress: () => router.replace('/minhas-candidaturas') },
      ]);
    } catch (err: any) {
      Alert.alert('Erro', err?.message || 'Falha ao submeter candidatura.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <MaterialCommunityIcons name="arrow-left" size={22} color="#1B1630" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Nova Candidatura</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <Text style={styles.subtitle}>Preencha os dados para se candidatar a um centro parceiro.</Text>

        {/* Course Selection */}
        <Text style={styles.label}>Curso pretendido *</Text>
        {loading ? (
          <ActivityIndicator size="small" color="#5B18E6" style={{ marginVertical: 12 }} />
        ) : (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.courseRow}>
            {courseList.map((course) => (
              <TouchableOpacity
                key={course.id}
                style={[styles.courseChip, selectedCourse === course.id && styles.courseChipActive]}
                onPress={() => setSelectedCourse(course.id)}
              >
                <Text style={[styles.courseChipText, selectedCourse === course.id && styles.courseChipTextActive]}>
                  {course.titulo}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        )}

        {/* Form Fields */}
        <Text style={styles.label}>Nome completo *</Text>
        <View style={styles.inputContainer}>
          <MaterialCommunityIcons name="account-outline" size={20} color="#9A93AD" />
          <TextInput style={styles.textInput} placeholder="Introduza o seu nome" placeholderTextColor="#8B8598" value={nome} onChangeText={setNome} />
        </View>

        <Text style={styles.label}>Email *</Text>
        <View style={styles.inputContainer}>
          <MaterialCommunityIcons name="email-outline" size={20} color="#9A93AD" />
          <TextInput style={styles.textInput} placeholder="exemplo@email.ao" placeholderTextColor="#8B8598" value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" />
        </View>

        <Text style={styles.label}>Telemóvel *</Text>
        <View style={styles.inputContainer}>
          <Text style={styles.phonePrefix}>+244</Text>
          <TextInput style={styles.textInput} placeholder="999 999 999" placeholderTextColor="#8B8598" value={telefone} onChangeText={setTelefone} keyboardType="phone-pad" />
        </View>

        <Text style={styles.label}>BI / Nº Identificação</Text>
        <View style={styles.inputContainer}>
          <MaterialCommunityIcons name="card-account-details-outline" size={20} color="#9A93AD" />
          <TextInput style={styles.textInput} placeholder="Opcional" placeholderTextColor="#8B8598" value={bi} onChangeText={setBi} />
        </View>

        {/* Document Upload */}
        <Text style={styles.label}>Documento de inscrição</Text>
        <TouchableOpacity style={styles.uploadBtn} onPress={() => pickDocument(setDocUri)}>
          <MaterialCommunityIcons name={docUri ? 'check-circle' : 'file-upload-outline'} size={20} color={docUri ? '#159B5E' : '#5B18E6'} />
          <Text style={[styles.uploadText, docUri && { color: '#159B5E' }]}>
            {docUri ? 'Documento selecionado' : 'Selecionar documento'}
          </Text>
        </TouchableOpacity>

        <Text style={styles.label}>Comprovativo de pagamento</Text>
        <TouchableOpacity style={styles.uploadBtn} onPress={() => pickDocument(setComprovativoUri)}>
          <MaterialCommunityIcons name={comprovativoUri ? 'check-circle' : 'receipt'} size={20} color={comprovativoUri ? '#159B5E' : '#5B18E6'} />
          <Text style={[styles.uploadText, comprovativoUri && { color: '#159B5E' }]}>
            {comprovativoUri ? 'Comprovativo selecionado' : 'Selecionar comprovativo'}
          </Text>
        </TouchableOpacity>

        {/* Submit */}
        <TouchableOpacity style={styles.submitBtn} onPress={handleSubmit} disabled={submitting}>
          {submitting ? (
            <ActivityIndicator color="#ffffff" />
          ) : (
            <Text style={styles.submitText}>Submeter Candidatura</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity onPress={() => router.push('/minhas-candidaturas')} style={styles.linkContainer}>
          <Text style={styles.linkText}>Ver minhas candidaturas</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F6F5FA' },
  header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 20, paddingVertical: 14, gap: 12 },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#ffffff', borderWidth: 1, borderColor: '#ECE8F3', alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontFamily: 'System', fontSize: 19, fontWeight: '800', color: '#1B1630' },
  content: { paddingHorizontal: 20, paddingBottom: 40 },
  subtitle: { fontFamily: 'System', fontSize: 13, fontWeight: '500', color: '#8B8598', marginBottom: 20 },
  label: { fontFamily: 'System', fontSize: 11, fontWeight: '700', color: '#4A4557', marginBottom: 6, marginTop: 14 },
  inputContainer: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#F5F3FB', borderWidth: 1, borderColor: '#E9E5F4', borderRadius: 14, paddingHorizontal: 15, paddingVertical: 14, marginBottom: 4, gap: 11 },
  textInput: { flex: 1, fontFamily: 'System', fontSize: 14, color: '#1B1630', padding: 0 },
  phonePrefix: { fontFamily: 'System', fontSize: 13, fontWeight: '700', color: '#4A4557' },
  courseRow: { gap: 10, paddingBottom: 4 },
  courseChip: { paddingHorizontal: 14, paddingVertical: 10, borderRadius: 12, backgroundColor: '#ffffff', borderWidth: 1.5, borderColor: '#ECE8F3' },
  courseChipActive: { backgroundColor: '#EDE7FE', borderColor: '#5B18E6' },
  courseChipText: { fontFamily: 'System', fontSize: 12, fontWeight: '600', color: '#8B8598' },
  courseChipTextActive: { color: '#5B18E6', fontWeight: '700' },
  uploadBtn: { flexDirection: 'row', alignItems: 'center', gap: 10, backgroundColor: '#F5F3FB', borderWidth: 1.5, borderColor: '#E9E5F4', borderStyle: 'dashed', borderRadius: 14, paddingVertical: 16, paddingHorizontal: 16, marginBottom: 4 },
  uploadText: { fontFamily: 'System', fontSize: 13, fontWeight: '600', color: '#5B18E6' },
  submitBtn: { backgroundColor: '#5B18E6', borderRadius: 15, paddingVertical: 16, alignItems: 'center', justifyContent: 'center', marginTop: 24, marginBottom: 12 },
  submitText: { fontFamily: 'System', fontSize: 15, fontWeight: '800', color: '#ffffff' },
  linkContainer: { alignItems: 'center', marginBottom: 20 },
  linkText: { fontFamily: 'System', fontSize: 13, fontWeight: '700', color: '#5B18E6' },
});
