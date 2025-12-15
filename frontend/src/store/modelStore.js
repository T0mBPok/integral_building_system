import { reactive, computed } from 'vue'
import { nanoid } from 'nanoid'

export const modelStore = reactive({
  mode: 'base', // base | weights | aggregate
  panelMode: 'base',
  selectedId: null,

  aggregateVisible: false, 

  aggregate: {
    id: 'aggregate',
    title: 'ЕДН',
    shortTitle: 'ЕДН',
    description: 'Итоговый демографический показатель',
    formula: 'R/N',
    normalizationMethod: 'minmax', // minmax | none | zscore ...
    exportFormat: 'txt'            // txt | csv и т.п.
  },
  
  weightsConfig: {
    title: 'Весовые коэффициенты',
    method: 'manual', // manual | expert | pairwise ...
    indicatorIds: []  // список id индикаторов, для которых считаем веса
  },

  indicators: []
})

export function addIndicator() {
  const id = nanoid()
  const randomValue = Math.floor(Math.random() * (1000 - 100 + 1)) + 100
  modelStore.indicators.push({
    id,
    title: 'Новый показатель',
    shortTitle: 'ПК',
    color: '#bfbfbf',
    description: '',

    // данные / формула базового показателя
    dataSources: [
      { code: 'R', name: 'Число рожденных' },
      { code: 'N', name: 'Численность населения в регионе' }
    ],
    range: {
      from: '2021',
      to: '2024'
    },
    formula: 'R/N',

    // значения после расчета
    value: randomValue,

    // параметры нормализации
    normalizationMethod: 'minmax',
    normalizationRange: { from: 0, to: 1 },

    // параметры веса (заполняются только в режиме "Рассчитать веса")
    weight: 1,
    weightLocked: false
  })
  modelStore.weightsConfig.indicatorIds.push(id)
  modelStore.selectedId = id
}

export const aggregatedValue = computed(() => {
  // весовая агрегация только если есть индикаторы
  const sum = modelStore.indicators.reduce((s, i) => s + (i.weight || 0), 0)
  if (!sum) return 0

  const values = modelStore.indicators.map(i => i.value);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const normalizedScore = modelStore.indicators.reduce(
    (res, i) => {
      const normalizedValue = (maxVal - minVal === 0) ? 0 : (i.value - minVal) / (maxVal - minVal);
      return res + (normalizedValue * i.weight) / sum;
    },
    0
  );
  return Number(normalizedScore.toFixed(2));
})

export function randomizeWeights() {
  const ids = modelStore.weightsConfig.indicatorIds
  if (!ids.length) return

  // генерим случайные положительные числа
  const temp = ids.map(() => Math.random())
  const sum = temp.reduce((s, v) => s + v, 0) || 1

  // нормируем так, чтобы сумма = 1
  ids.forEach((id, idx) => {
    const ind = modelStore.indicators.find(i => i.id === id)
    if (!ind) return
    ind.weight = +(temp[idx] / sum).toFixed(3) // например, 3 знака
  })
}
