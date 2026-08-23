import {useCallback, useEffect, useState} from "react";
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import {api, Dashboard, formatMoney, Transaction} from "./src/api";

type Tab = "home" | "transactions" | "new" | "cards" | "more";

const tabs: {id: Tab; label: string; icon: string}[] = [
  {id: "home", label: "Início", icon: "⌂"},
  {id: "transactions", label: "Movimentos", icon: "↕"},
  {id: "new", label: "Novo", icon: "+"},
  {id: "cards", label: "Cartões", icon: "▣"},
  {id: "more", label: "Mais", icon: "•••"},
];

export default function App() {
  const [tab, setTab] = useState<Tab>("home");
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setError("");
      const [summary, items] = await Promise.all([
        api<Dashboard>("/dashboard"),
        api<Transaction[]>("/transactions?limit=40"),
      ]);
      setDashboard(summary);
      setTransactions(items);
    } catch {
      setError("Não foi possível conectar ao FinanSys. Confira o endereço da API.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="dark-content" />
      <View style={styles.header}>
        <View><Text style={styles.eyebrow}>FINANSYS</Text><Text style={styles.title}>{title(tab)}</Text></View>
        <View style={styles.avatar}><Text style={styles.avatarText}>F</Text></View>
      </View>
      {loading ? <ActivityIndicator style={styles.loader} color="#1d4ed8" /> : (
        <ScrollView
          contentContainerStyle={styles.content}
          refreshControl={<RefreshControl refreshing={false} onRefresh={load} />}
          keyboardShouldPersistTaps="handled"
        >
          {error ? <Text style={styles.error}>{error}</Text> : null}
          {tab === "home" && dashboard ? <Home data={dashboard} /> : null}
          {tab === "transactions" ? <Transactions items={transactions} /> : null}
          {tab === "new" ? <NewTransaction onSaved={() => { setTab("home"); load(); }} /> : null}
          {tab === "cards" ? <Cards /> : null}
          {tab === "more" ? <More /> : null}
        </ScrollView>
      )}
      <View style={styles.tabBar}>
        {tabs.map((item) => (
          <Pressable key={item.id} onPress={() => setTab(item.id)} style={styles.tab}>
            <View style={[item.id === "new" && styles.addButton, tab === item.id && item.id !== "new" && styles.tabActive]}>
              <Text style={[styles.tabIcon, item.id === "new" && styles.addIcon]}>{item.icon}</Text>
            </View>
            <Text style={[styles.tabLabel, tab === item.id && styles.tabLabelActive]}>{item.label}</Text>
          </Pressable>
        ))}
      </View>
    </SafeAreaView>
  );
}

function Home({data}: {data: Dashboard}) {
  return <>
    <View style={styles.balanceCard}>
      <Text style={styles.balanceLabel}>Saldo deste mês</Text>
      <Text style={styles.balanceValue}>{formatMoney(data.balance)}</Text>
      <View style={styles.balanceRow}>
        <Text style={styles.income}>↑ {formatMoney(data.income)}</Text>
        <Text style={styles.expense}>↓ {formatMoney(data.expenses)}</Text>
      </View>
    </View>
    <SectionTitle title="Movimentos recentes" />
    <TransactionList items={data.recent_transactions} />
    {data.alerts.length ? <><SectionTitle title="Atenção" />{data.alerts.map((alert, index) => <Text key={index} style={styles.alert}>{alert.text}</Text>)}</> : null}
  </>;
}

function Transactions({items}: {items: Transaction[]}) {
  return <><Text style={styles.helper}>Deslize para atualizar e acompanhe seus lançamentos.</Text><TransactionList items={items} /></>;
}

function TransactionList({items}: {items: Transaction[]}) {
  return <View style={styles.list}>{items.length ? items.map((item) => (
    <View key={item.id} style={styles.transaction}>
      <View style={[styles.transactionIcon, item.kind === "income" ? styles.incomeBg : styles.expenseBg]}><Text>{item.kind === "income" ? "↑" : "↓"}</Text></View>
      <View style={styles.transactionMain}><Text style={styles.transactionTitle}>{item.description}</Text><Text style={styles.transactionDate}>{new Date(`${item.occurred_on}T12:00:00`).toLocaleDateString("pt-BR")}</Text></View>
      <Text style={item.kind === "income" ? styles.income : styles.expense}>{item.kind === "income" ? "+" : "−"}{formatMoney(item.amount)}</Text>
    </View>
  )) : <Text style={styles.empty}>Ainda não há lançamentos.</Text>}</View>;
}

function NewTransaction({onSaved}: {onSaved: () => void}) {
  const [kind, setKind] = useState<"expense" | "income">("expense");
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const save = async () => {
    const value = Number(amount.replace(",", "."));
    if (!description.trim() || !value) return setMessage("Preencha descrição e valor.");
    setSaving(true);
    try {
      await api("/transactions", {method: "POST", body: JSON.stringify({description, amount: value, occurred_on: new Date().toISOString().slice(0, 10), kind, installments_total: 1})});
      onSaved();
    } catch { setMessage("Não foi possível salvar o lançamento."); }
    finally { setSaving(false); }
  };
  return <View style={styles.formCard}>
    <View style={styles.segmented}>
      {(["expense", "income"] as const).map((value) => <Pressable key={value} onPress={() => setKind(value)} style={[styles.segment, kind === value && styles.segmentActive]}><Text style={kind === value && styles.segmentTextActive}>{value === "expense" ? "Despesa" : "Receita"}</Text></Pressable>)}
    </View>
    <Text style={styles.label}>Descrição</Text><TextInput value={description} onChangeText={setDescription} placeholder="Ex.: Supermercado" style={styles.input} />
    <Text style={styles.label}>Valor</Text><TextInput value={amount} onChangeText={setAmount} placeholder="0,00" keyboardType="decimal-pad" style={styles.input} />
    {message ? <Text style={styles.error}>{message}</Text> : null}
    <Pressable onPress={save} disabled={saving} style={styles.primaryButton}><Text style={styles.primaryButtonText}>{saving ? "Salvando…" : "Salvar lançamento"}</Text></Pressable>
  </View>;
}

function Cards() { return <RemoteCollection endpoint="/cards" empty="Nenhum cartão ativo." />; }
function More() { return <><SectionTitle title="Metas" /><RemoteCollection endpoint="/goals" empty="Nenhuma meta ativa." /><SectionTitle title="Assinaturas" /><RemoteCollection endpoint="/subscriptions" empty="Nenhuma assinatura ativa." /></>; }

function RemoteCollection({endpoint, empty}: {endpoint: string; empty: string}) {
  const [items, setItems] = useState<{id: number; name: string; amount?: number; target_amount?: number}[]>([]);
  useEffect(() => { api<typeof items>(endpoint).then(setItems).catch(() => setItems([])); }, [endpoint]);
  return <View style={styles.list}>{items.length ? items.map((item) => <View key={item.id} style={styles.simpleRow}><Text style={styles.transactionTitle}>{item.name}</Text>{item.amount != null ? <Text>{formatMoney(item.amount)}</Text> : item.target_amount != null ? <Text>{formatMoney(item.target_amount)}</Text> : null}</View>) : <Text style={styles.empty}>{empty}</Text>}</View>;
}

function SectionTitle({title: value}: {title: string}) { return <Text style={styles.sectionTitle}>{value}</Text>; }
function title(tab: Tab) { return {home: "Visão geral", transactions: "Movimentações", new: "Novo lançamento", cards: "Cartões", more: "Planejamento"}[tab]; }

const styles = StyleSheet.create({
  safe: {flex: 1, backgroundColor: "#f4f7fb"}, header: {paddingHorizontal: 20, paddingVertical: 14, flexDirection: "row", alignItems: "center", justifyContent: "space-between"}, eyebrow: {fontSize: 10, letterSpacing: 1.4, color: "#64748b", fontWeight: "700"}, title: {fontSize: 25, color: "#13213a", fontWeight: "800", marginTop: 4}, avatar: {width: 38, height: 38, borderRadius: 14, backgroundColor: "#dbeafe", alignItems: "center", justifyContent: "center"}, avatarText: {color: "#1d4ed8", fontWeight: "800"}, content: {padding: 20, paddingBottom: 110}, loader: {flex: 1}, balanceCard: {backgroundColor: "#1d4ed8", padding: 22, borderRadius: 24}, balanceLabel: {color: "#bfdbfe", fontSize: 13}, balanceValue: {color: "white", fontSize: 32, fontWeight: "800", marginTop: 8}, balanceRow: {flexDirection: "row", gap: 18, marginTop: 18}, sectionTitle: {fontSize: 17, fontWeight: "800", color: "#13213a", marginTop: 26, marginBottom: 12}, list: {backgroundColor: "white", borderRadius: 18, overflow: "hidden"}, transaction: {padding: 14, flexDirection: "row", alignItems: "center", borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: "#e2e8f0"}, transactionIcon: {width: 40, height: 40, borderRadius: 13, alignItems: "center", justifyContent: "center"}, incomeBg: {backgroundColor: "#dcfce7"}, expenseBg: {backgroundColor: "#fee2e2"}, transactionMain: {flex: 1, marginHorizontal: 11}, transactionTitle: {fontSize: 14, fontWeight: "700", color: "#13213a"}, transactionDate: {fontSize: 11, color: "#64748b", marginTop: 3}, income: {color: "#15803d", fontWeight: "700"}, expense: {color: "#dc2626", fontWeight: "700"}, alert: {backgroundColor: "#fffbeb", color: "#92400e", padding: 13, borderRadius: 13, marginBottom: 8}, helper: {color: "#64748b", marginBottom: 14}, empty: {padding: 24, textAlign: "center", color: "#64748b"}, error: {backgroundColor: "#fee2e2", color: "#991b1b", padding: 12, borderRadius: 12, marginBottom: 12}, formCard: {backgroundColor: "white", padding: 18, borderRadius: 20}, segmented: {flexDirection: "row", backgroundColor: "#f1f5f9", borderRadius: 12, padding: 4, marginBottom: 18}, segment: {flex: 1, padding: 10, borderRadius: 9, alignItems: "center"}, segmentActive: {backgroundColor: "#1d4ed8"}, segmentTextActive: {color: "white", fontWeight: "700"}, label: {fontSize: 12, color: "#475569", fontWeight: "700", marginBottom: 6, marginTop: 12}, input: {height: 50, borderWidth: 1, borderColor: "#dce3ed", borderRadius: 12, paddingHorizontal: 14, fontSize: 16}, primaryButton: {height: 50, backgroundColor: "#1d4ed8", borderRadius: 13, alignItems: "center", justifyContent: "center", marginTop: 22}, primaryButtonText: {color: "white", fontWeight: "800"}, simpleRow: {padding: 16, flexDirection: "row", justifyContent: "space-between", borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: "#e2e8f0"}, tabBar: {position: "absolute", left: 0, right: 0, bottom: 0, height: 82, paddingBottom: 12, backgroundColor: "white", borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: "#cbd5e1", flexDirection: "row"}, tab: {flex: 1, alignItems: "center", justifyContent: "center"}, tabIcon: {fontSize: 21, color: "#64748b"}, tabActive: {backgroundColor: "#dbeafe", width: 38, height: 30, borderRadius: 11, alignItems: "center", justifyContent: "center"}, tabLabel: {fontSize: 9, color: "#64748b", marginTop: 4}, tabLabelActive: {color: "#1d4ed8", fontWeight: "800"}, addButton: {width: 52, height: 52, marginTop: -28, borderRadius: 18, backgroundColor: "#1d4ed8", alignItems: "center", justifyContent: "center"}, addIcon: {fontSize: 30, color: "white"}
});
