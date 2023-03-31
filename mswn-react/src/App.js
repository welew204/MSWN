import "./App.css";
import { useState } from "react";
import { Route, Routes } from "react-router-dom";
import MoverSelect from "./components/MoverSelect";
import RecordWkout from "./components/RecordWkout";
import WkoutBuilder from "./components/WkoutBuilder";
import StatusView from "./components/StatusView";
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from "@tanstack/react-query";

import Home from "./components/Home";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import Coaches from "./components/Coaches";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route path='/coaches' element={<Coaches />} />
        <Route path='/' element={<Home />}>
          <Route index element={<MoverSelect />} />
          <Route path='/mover' element={<MoverSelect />} />
          <Route path='/wbuilder' element={<WkoutBuilder />} />
          <Route path='/record' element={<RecordWkout />} />
          <Route path='/status' element={<StatusView />} />
        </Route>
      </Routes>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
