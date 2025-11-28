import { Overview } from "@/components/overview";

export default function Home() {
    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6">
                    <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <h3 className="tracking-tight text-sm font-medium">Total Reports</h3>
                    </div>
                    <div className="text-2xl font-bold">150</div>
                    <p className="text-xs text-muted-foreground">+20.1% from last month</p>
                </div>
                <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6">
                    <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <h3 className="tracking-tight text-sm font-medium">Resolved</h3>
                    </div>
                    <div className="text-2xl font-bold">120</div>
                    <p className="text-xs text-muted-foreground">+180.1% from last month</p>
                </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <div className="col-span-4 rounded-xl border bg-card text-card-foreground shadow-sm p-6">
                    <div className="flex flex-col space-y-1.5 p-6 pl-0 pt-0">
                        <h3 className="font-semibold leading-none tracking-tight">Overview</h3>
                    </div>
                    <div className="pl-2">
                        <Overview />
                    </div>
                </div>
            </div>
        </div>
    );
}
