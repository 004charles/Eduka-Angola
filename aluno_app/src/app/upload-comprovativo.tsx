import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, StatusBar, Alert } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import { cursos } from '@/services/api';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
};

export default function UploadComprovativoScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ cursoId?: string }>();
  const cursoId = params.cursoId ? Number(params.cursoId) : undefined;

  const [imageUri, setImageUri] = useState<string | null>(null);
  const [imageName, setImageName] = useState<string>('');
  const [uploading, setUploading] = useState(false);

  const pickFromGallery = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permissão necessária', 'Autorize o acesso à galeria nas definições.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.8,
    });
    if (!result.canceled && result.assets[0]) {
      setImageUri(result.assets[0].uri);
      setImageName(result.assets[0].uri.split('/').pop() || 'imagem.jpg');
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permissão necessária', 'Autorize o acesso à câmara nas definições.');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'],
      quality: 0.8,
    });
    if (!result.canceled && result.assets[0]) {
      setImageUri(result.assets[0].uri);
      setImageName(result.assets[0].uri.split('/').pop() || 'foto.jpg');
    }
  };

  const handleUpload = async () => {
    if (!cursoId) {
      Alert.alert('Erro', 'Curso não identificado.');
      return;
    }
    if (!imageUri) {
      Alert.alert('Erro', 'Selecione ou tire uma foto do comprovativo.');
      return;
    }
    setUploading(true);
    try {
      await cursos.enviarComprovativo(cursoId, imageUri);
      Alert.alert('Sucesso', 'Comprovativo enviado com sucesso!', [
        { text: 'OK', onPress: () => router.back() },
      ]);
    } catch (err: any) {
      Alert.alert('Erro', err.message || 'Não foi possível enviar o comprovativo.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Enviar comprovativo</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <Text style={styles.description}>
          Envie o comprovativo de pagamento para que a sua inscrição seja processada. Aceitamos imagens (JPG, PNG) ou documentos PDF.
        </Text>

        {/* Upload Area */}
        <TouchableOpacity style={styles.uploadArea} activeOpacity={0.7} onPress={pickFromGallery}>
          <View style={styles.uploadIconWrap}>
            <MaterialCommunityIcons name="camera-outline" size={40} color={COLORS.purple} />
          </View>
          <Text style={styles.uploadTitle}>Tirar fotografia</Text>
          <Text style={styles.uploadSubtitle}>ou escolher da galeria</Text>
        </TouchableOpacity>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.actionBtn} activeOpacity={0.7} onPress={takePhoto}>
            <MaterialCommunityIcons name="camera" size={20} color={COLORS.purple} />
            <Text style={styles.actionBtnText}>Câmara</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.actionBtn, styles.actionBtnSecondary]} activeOpacity={0.7} onPress={pickFromGallery}>
            <MaterialCommunityIcons name="image-multiple" size={20} color={COLORS.purple} />
            <Text style={styles.actionBtnText}>Galeria</Text>
          </TouchableOpacity>
        </View>

        {/* Uploaded File */}
        {imageUri && (
          <View style={styles.uploadedCard}>
            <View style={styles.fileIconWrap}>
              <MaterialCommunityIcons name="file-image" size={24} color={COLORS.purple} />
            </View>
            <View style={styles.fileInfo}>
              <Text style={styles.fileName}>{imageName}</Text>
              <Text style={styles.fileMeta}>Selecionado</Text>
            </View>
            <View style={styles.checkCircle}>
              <MaterialCommunityIcons name="check" size={16} color="#fff" />
            </View>
          </View>
        )}

        {/* Status Badge */}
        {!imageUri && (
          <View style={styles.statusBadge}>
            <View style={styles.statusDot} />
            <Text style={styles.statusText}>Estado: Aguardando comprovativo</Text>
          </View>
        )}

        {/* Submit Button */}
        <TouchableOpacity
          style={[styles.submitBtn, (uploading || !imageUri) && { opacity: 0.6 }]}
          activeOpacity={0.8}
          onPress={handleUpload}
          disabled={uploading || !imageUri}
        >
          <Text style={styles.submitBtnText}>
            {uploading ? 'A enviar...' : 'Enviar comprovativo'}
          </Text>
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
  description: {
    fontSize: 14,
    color: COLORS.gray,
    fontFamily: 'System',
    lineHeight: 21,
    marginBottom: 24,
  },
  uploadArea: {
    borderWidth: 2,
    borderColor: COLORS.border,
    borderStyle: 'dashed',
    borderRadius: 16,
    paddingVertical: 32,
    alignItems: 'center',
    backgroundColor: '#fff',
    marginBottom: 16,
  },
  uploadIconWrap: {
    width: 72,
    height: 72,
    borderRadius: 20,
    backgroundColor: COLORS.lightPurple,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  uploadTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.dark,
    fontFamily: 'System',
    marginBottom: 4,
  },
  uploadSubtitle: {
    fontSize: 13,
    color: COLORS.gray,
    fontFamily: 'System',
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  actionBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: COLORS.lightPurple,
    borderRadius: 12,
    paddingVertical: 14,
    borderWidth: 1.5,
    borderColor: COLORS.purple,
  },
  actionBtnSecondary: {
    backgroundColor: '#fff',
    borderColor: COLORS.border,
  },
  actionBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: COLORS.purple,
    fontFamily: 'System',
  },
  uploadedCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 12,
  },
  fileIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: COLORS.lightPurple,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  fileInfo: {
    flex: 1,
  },
  fileName: {
    fontSize: 15,
    fontWeight: '600',
    color: COLORS.dark,
    fontFamily: 'System',
    marginBottom: 2,
  },
  fileMeta: {
    fontSize: 13,
    color: COLORS.gray,
    fontFamily: 'System',
  },
  checkCircle: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#22C55E',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: '#FEF3C7',
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 8,
    marginBottom: 28,
    gap: 8,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#F59E0B',
  },
  statusText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#92400E',
    fontFamily: 'System',
  },
  submitBtn: {
    backgroundColor: COLORS.purple,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
    shadowColor: COLORS.purple,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  submitBtnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
    fontFamily: 'System',
  },
});
