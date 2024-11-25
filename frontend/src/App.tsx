import './App.css'
import { Outlet } from "react-router-dom";
import { ApplicationContextProvider } from "@/components/util/ApplicationContextProvider.tsx";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar.tsx";
import { MainSidebar } from "@/components/Navigation/MainSidebar.tsx";

function App() {
  return (
    <ApplicationContextProvider>
      <SidebarProvider>
        <MainSidebar />
        <SidebarInset>
        <div className="flex flex-col grow">
          <Outlet/>
        </div>
        </SidebarInset>
      </SidebarProvider>
    </ApplicationContextProvider>
  )
}

export default App
