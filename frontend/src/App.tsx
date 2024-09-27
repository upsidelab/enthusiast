import './App.css'
import { Sidebar } from "@/components/Navigation/Sidebar.tsx";
import { MainMenu } from "@/components/Navigation/MainMenu.tsx";
import { Outlet } from "react-router-dom";
import { ApplicationContextProvider } from "@/components/util/ApplicationContextProvider.tsx";

function App() {
  return (
    <ApplicationContextProvider>
      <div className="h-full flex flex-col">
        <MainMenu/>
        <div className="grid lg:grid-cols-5 flex-1">
          <Sidebar/>
          <div className="col-span-3 lg:col-span-4 lg:border-l">
            <Outlet/>
          </div>
        </div>
      </div>
    </ApplicationContextProvider>
  )
}

export default App
