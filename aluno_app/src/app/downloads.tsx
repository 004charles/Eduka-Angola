import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, Switch, StatusBar, ActivityIndicator } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import * as FileSystem from 'expo-file-system';
import { materiais } from '@/services/api';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
  green: '#159B5E',
};

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(0)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

export default function DownloadsScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ cursoId?: string; courseId?: string }>();
  const cursoId = params.cursoId || params.courseId || '1';

  const [wifiOnly, setWifiOnly] = useState(true);
  const [loading, setLoading] = useState(true);
  const [materials, setMaterials] = useState<any[]>([]);
  const [downloading, setDownloading] = useState<Record<string, number>>({});
  const [downloadedFiles, setDownloadedFiles] = useState<Record<string, FileSystem.FileInfo>>({});

  const totalGB = 4;
  const usedBytes = Object.values(downloadedFiles).reduce((acc, f) => acc + (f.exists ? f.size || 0 : 0), 0);
  const usedGB = parseFloat((usedBytes / (1024 * 1024 * 1024)).toFixed(1));
  const usagePercent = Math.min((usedGB / totalGB) * 100, 100);

  useEffect(() => {
    loadMaterials();
  }, [cursoId]);

  async function loadMaterials() {
    try {
      setLoading(true);
      const data = await materiais.list(cursoId);
      const list = Array.isArray(data) ? data : data?.results || [];
      setMaterials(list);

      const downloaded: Record<string, FileSystem.FileInfo> = {};
      for (const item of list) {
        const fileName = item.nome || item.filename || `material_${item.id}`;
        const fileUri = `${FileSystem.documentDirectory}${fileName}`;
        try {
          const info = await FileSystem.getInfoAsync(fileUri);
          if (info.exists) {
            downloaded[item.id] = info;
          }
        } catch {}
      }
      setDownloadedFiles(downloaded);
    } catch (err) {
      console.error('Erro ao carregar materiais:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleDownload(item: any) {
    const url = item.url || item.arquivo || item.file_url;
    const fileName = item.nome || item.filename || `material_${item.id}`;
    const fileUri = `${FileSystem.documentDirectory}${fileName}`;

    if (!url) return;

    try {
      setDownloading((prev) => ({ ...prev, [item.id]: 0 }));
      const downloadResumable = FileSystem.createDownloadResumable(
        url,
        fileUri,
        {},
        (downloadProgress) => {
          const progress = downloadProgress.totalBytesWritten / downloadProgress.totalBytesExpectedToWrite;
          setDownloading((prev) => ({ ...prev, [item.id]: Math.round(progress * 100) }));
        }
      );

      const result = await downloadResumable.downloadAsync();
      if (result) {
        const info = await FileSystem.getInfoAsync(fileUri);
        setDownloadedFiles((prev) => ({ ...prev, [item.id]: info }));
      }
    } catch (err) {
      console.error('Erro ao descarregar:', err);
    } finally {
      setDownloading((prev) => {
        const next = { ...prev };
        delete next[item.id];
        return next;
      });
    }
  }

  async function handleDelete(item: any) {
    const fileName = item.nome || item.filename || `material_${item.id}`;
    const fileUri = `${FileSystem.documentDirectory}${fileName}`;
    try {
      await FileSystem.deleteAsync(fileUri, { idempotent: true });
      setDownloadedFiles((prev) => {
        const next = { ...prev };
        delete next[item.id];
        return next;
      });
    } catch (err) {
      console.error('Erro ao eliminar:', err);
    }
  }

  const completedMaterials = materials.filter((m) => downloadedFiles[m.id]);
  const downloadingMaterials = materials.filter((m) => downloading[m.id] !== undefined);
  const pendingMaterials = materials.filter((m) => !downloadedFiles[m.id] && downloading[m.id] === undefined);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <MaterialCommunityIcons name="arrow-left" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Downloads</Text>
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <ActivityIndicator size="large" color={COLORS.purple} />
        </View>
      ) : (
        <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
          {/* Storage Bar */}
          <View style={styles.storageCard}>
            <View style={styles.storageHeader}>
              <MaterialCommunityIcons name="cloud-download-outline" size={22} color={COLORS.purple} />
              <Text style={styles.storageText}>{usedGB} GB de {totalGB} GB</Text>
            </View>
            <View style={styles.storageTrack}>
              <View style={[styles.storageFill, { width: `${usagePercent}%` }]} />
            </View>
          </View>

          {/* WiFi Toggle */}
          <View style={styles.toggleRow}>
            <Text style={styles.toggleLabel}>Descarregar apenas em Wi-Fi</Text>
            <Switch
              value={wifiOnly}
              onValueChange={setWifiOnly}
              trackColor={{ false: COLORS.border, true: COLORS.purple }}
              thumbColor="#fff"
            />
          </View>

          {/* Downloaded Section */}
          {completedMaterials.length > 0 && (
            <>
              <Text style={styles.sectionTitle}>Aulas descarregadas</Text>
              {completedMaterials.map((item) => {
                const fileName = item.nome || item.filename || `material_${item.id}`;
                const fileSize = item.tamanho || item.size || downloadedFiles[item.id]?.size || 0;
                return (
                  <View key={item.id} style={styles.downloadCard}>
                    <View style={styles.downloadIconWrap}>
                      <MaterialCommunityIcons name="download-done" size={24} color={COLORS.green} />
                    </View>
                    <View style={styles.downloadInfo}>
                      <Text style={styles.downloadTitle}>{item.titulo || item.title || fileName}</Text>
                      <Text style={styles.downloadMeta}>
                        {item.curso_nome || item.course || ''} · {formatSize(fileSize)}
                      </Text>
                    </View>
                    <TouchableOpacity style={styles.deleteBtn} onPress={() => handleDelete(item)}>
                      <MaterialCommunityIcons name="delete-outline" size={22} color={COLORS.gray} />
                    </TouchableOpacity>
                  </View>
                );
              })}
            </>
          )}

          {/* Downloading Section */}
          {downloadingMaterials.map((item) => {
            const progress = downloading[item.id] || 0;
            return (
              <View key={item.id} style={styles.downloadCard}>
                <View style={styles.downloadingIconWrap}>
                  <MaterialCommunityIcons name="download" size={24} color={COLORS.purple} />
                </View>
                <View style={styles.downloadInfo}>
                  <Text style={styles.downloadTitle}>{item.titulo || item.title || item.nome || item.filename}</Text>
                  <Text style={styles.downloadMeta}>A descarregar · {progress}%</Text>
                  <View style={styles.miniProgressTrack}>
                    <View style={[styles.miniProgressFill, { width: `${progress}%` }]} />
                  </View>
                </View>
                <TouchableOpacity style={styles.closeBtn}>
                  <MaterialCommunityIcons name="close" size={20} color={COLORS.gray} />
                </TouchableOpacity>
              </View>
            );
          })}

          {/* Available for download */}
          {pendingMaterials.length > 0 && (
            <>
              <Text style={[styles.sectionTitle, { marginTop: 16 }]}>Materiais disponíveis</Text>
              {pendingMaterials.map((item) => {
                const fileName = item.nome || item.filename || `material_${item.id}`;
                const fileSize = item.tamanho || item.size || 0;
                return (
                  <TouchableOpacity
                    key={item.id}
                    style={styles.downloadCard}
                    onPress={() => handleDownload(item)}
                    activeOpacity={0.7}
                  >
                    <View style={styles.downloadingIconWrap}>
                      <MaterialCommunityIcons name="file-download-outline" size={24} color={COLORS.purple} />
                    </View>
                    <View style={styles.downloadInfo}>
                      <Text style={styles.downloadTitle}>{item.titulo || item.title || fileName}</Text>
                      <Text style={styles.downloadMeta}>
                        {item.tipo || item.type || 'Material'} · {fileSize ? formatSize(fileSize) : ''}
                      </Text>
                    </View>
                    <MaterialCommunityIcons name="download" size={22} color={COLORS.purple} />
                  </TouchableOpacity>
                );
              })}
            </>
          )}

          {materials.length === 0 && (
            <View style={{ alignItems: 'center', marginTop: 60 }}>
              <MaterialCommunityIcons name="file-off-outline" size={48} color={COLORS.gray} />
              <Text style={{ fontSize: 14, color: COLORS.gray, marginTop: 12, fontFamily: 'System' }}>
                Sem materiais disponíveis
              </Text>
            </View>
          )}

          <View style={{ height: 40 }} />
        </ScrollView>
      )}
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
  storageCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 16,
  },
  storageHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 12,
  },
  storageText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  storageTrack: {
    height: 8,
    backgroundColor: COLORS.border,
    borderRadius: 4,
  },
  storageFill: {
    height: '100%',
    backgroundColor: COLORS.purple,
    borderRadius: 4,
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 24,
  },
  toggleLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: COLORS.gray,
    fontFamily: 'System',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 12,
  },
  downloadCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 10,
    gap: 12,
  },
  downloadIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: '#E6F9EE',
    justifyContent: 'center',
    alignItems: 'center',
  },
  downloadingIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: COLORS.lightPurple,
    justifyContent: 'center',
    alignItems: 'center',
  },
  downloadInfo: {
    flex: 1,
  },
  downloadTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.dark,
    fontFamily: 'System',
    marginBottom: 2,
  },
  downloadMeta: {
    fontSize: 12,
    color: COLORS.gray,
    fontFamily: 'System',
  },
  miniProgressTrack: {
    height: 4,
    backgroundColor: COLORS.border,
    borderRadius: 2,
    marginTop: 8,
  },
  miniProgressFill: {
    height: '100%',
    backgroundColor: COLORS.purple,
    borderRadius: 2,
  },
  deleteBtn: {
    padding: 6,
  },
  closeBtn: {
    padding: 6,
  },
});
