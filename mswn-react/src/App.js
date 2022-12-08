import './App.css';
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from "@tanstack/react-query";
import BoutLogForm from './components/BoutLogForm';

const queryClient = new QueryClient();

function App() {

  return (
    <QueryClientProvider client={queryClient}>
      <BoutLogForm/>
    </QueryClientProvider>
  );
}

export default App;
