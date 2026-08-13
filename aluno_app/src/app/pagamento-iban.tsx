import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, StatusBar, Alert } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
};

const ibanFields = [
  { label: 'BANCO', value: 'BFA' },
  { label: 'IBAN', value: 'AO06 0006 0000 0100 0378 4121 4' },
  { label: 'TITULAR', value: 'EdukAngola, Lda.' },
  { label: 'REFERÊNCIA', value: 'EDU-8F3A9' },
  { label: 'VALOR', value: '45.000 Kz' },
];

export default function PagamentoIBANScreen() {
  const router = useRouter();

  const handleCopy = (text: string) => {
    Alert.alert('Copiado', `"${text}" copiado para a área de transferência.`);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Dados para transferência</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Info Banner */}
        <View style={styles.infoBanner}>
          <MaterialCommunityIcons name="information-outline" size={20} color="#fff" />
          <Text style={styles.infoBannerText}>
            Envie o comprovativo de transferência para o e-mail ou WhatsApp da EdukAngola após efetuar o pagamento.
          </Text>
        </View>

        {/* IBAN Card */}
        <View style={styles.ibanCard}>
          {ibanFields.map((field, index) => {
            const showCopy = field.label === 'IBAN' || field.label === 'REFERÊNCIA';
            return (
              <View key={field.label}>
                <View style={styles.fieldRow}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.fieldLabel}>{field.label}</Text>
                    <Text style={styles.fieldValue}>{field.value}</Text>
                  </View>
                  {showCopy && (
                    <TouchableOpacity
                      style={styles.copyBtn}
                      onPress={() => handleCopy(field.value)}
                      activeOpacity={0.7}
                    >
                      <MaterialCommunityIcons name="content-copy" size={18} color={COLORS.purple} />
                    </TouchableOpacity>
                  )}
                </View>
                {index < ibanFields.length - 1 && <View style={styles.fieldDivider} />}
              </View>
            );
          })}
        </View>

        {/* Pay Button */}
        <TouchableOpacity style={styles.payBtn} activeOpacity={0.8}>
          <MaterialCommunityIcons name="check-circle-outline" size={20} color="#fff" />
          <Text style={styles.payBtnText}>Já efetuei o pagamento</Text>
        </TouchableOpacity>

        <View style={{ height: 40 }} />
      </ScrollView>
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
    backgroundColor: COLORS.bg,
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
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 20,
  },
  infoBanner: {
    flexDirection: 'row',
    backgroundColor: COLORS.purple,
    borderRadius: 14,
    padding: 16,
    marginBottom: 20,
    alignItems: 'flex-start',
    gap: 10,
  },
  infoBannerText: {
    flex: 1,
    fontSize: 13,
    color: '#fff',
    fontFamily: 'System',
    lineHeight: 19,
  },
  ibanCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 24,
  },
  fieldRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
  },
  fieldLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: COLORS.gray,
    fontFamily: 'System',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  fieldValue: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  copyBtn: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: COLORS.lightPurple,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 12,
  },
  fieldDivider: {
    height: 1,
    backgroundColor: COLORS.border,
  },
  payBtn: {
    backgroundColor: COLORS.purple,
    borderRadius: 14,
    paddingVertical: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
    shadowColor: COLORS.purple,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  payBtnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
    fontFamily: 'System',
  },
});
