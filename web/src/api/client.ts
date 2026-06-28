import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export const getSnapshotCurrent = async () => {
  const response = await api.get('/snapshots/current');
  return response.data;
};

export const submitMatchResult = async (result: any) => {
  const response = await api.post('/admin/match', result);
  return response.data;
};

export const triggerSimulation = async (params: any = {}) => {
  const response = await api.post('/admin/simulate', params);
  return response.data;
};

export const getMatchPrediction = async (home: string, away: string) => {
  const response = await api.get(`/predictions/match?home=${home}&away=${away}`);
  return response.data;
};

export const runWhatIf = async (homeTeamId: string, awayTeamId: string, homeGoals: number, awayGoals: number) => {
  const response = await api.post('/admin/what-if', {
    homeTeamId,
    awayTeamId,
    homeGoals,
    awayGoals
  });
  return response.data;
};

export const getUpsets = async () => {
  const response = await api.get('/upsets');
  return response.data;
};

export const getTournamentMatches = async () => {
  const response = await api.get('/tournament/matches');
  return response.data;
};

export const getTournamentGroups = async () => {
  const response = await api.get('/tournament/groups');
  return response.data;
};

export const getTournamentBracket = async () => {
  const response = await api.get('/tournament/bracket');
  return response.data;
};

export const getDeltas = async (model: string, metric: string, team?: string) => {
  const url = team 
    ? `/snapshots/deltas?model=${model}&metric=${metric}&team=${team}`
    : `/snapshots/deltas?model=${model}&metric=${metric}`;
  const response = await api.get(url);
  return response.data;
};
