"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import MobileNav from "@/components/layout/MobileNav";
import Card, { CardHeader } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import { Save, Hotel, Globe, Phone, Mail, MapPin } from "lucide-react";
import type { Hotel as HotelType } from "@/lib/types";

const DEMO_HOTELS: HotelType[] = [
  { id: "demo-1", name: "Kandy Heritage Villa", slug: "kandy-heritage-villa", city: "Kandy", district: "Kandy", star_rating: 4, total_rooms: 12, minimum_rate_lkr: 8000, amenities: ["WiFi", "Pool", "Restaurant", "Spa", "Airport Transfer", "Parking", "Room Service", "Laundry"], is_active: true, contact_email: "reservations@kandyheritagevilla.lk", contact_phone: "+94812234567", whatsapp_number: "+94771234567", address: "45 Temple Road, Peradeniya", created_at: "", updated_at: "" },
];

export default function SettingsPage() {
  const [selectedHotel] = useState(DEMO_HOTELS[0]);
  const [darkMode, setDarkMode] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: selectedHotel.name,
    city: selectedHotel.city || "",
    address: selectedHotel.address || "",
    contact_email: selectedHotel.contact_email || "",
    contact_phone: selectedHotel.contact_phone || "",
    whatsapp_number: selectedHotel.whatsapp_number || "",
    total_rooms: selectedHotel.total_rooms,
    minimum_rate_lkr: selectedHotel.minimum_rate_lkr,
    star_rating: selectedHotel.star_rating || 4,
  });

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  const handleSave = async () => {
    setSaving(true);
    // Simulate save
    await new Promise(r => setTimeout(r, 1000));
    setSaving(false);
  };

  const inputClass = "w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-foreground dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent transition-all";
  const labelClass = "block text-sm font-medium text-foreground dark:text-gray-300 mb-1.5";

  return (
    <div className="flex min-h-screen bg-background dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 lg:ml-64">
        <Header hotels={DEMO_HOTELS} selectedHotel={selectedHotel} onSelectHotel={() => {}} darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />
        <main className="p-4 md:p-6 lg:p-8 pb-24 lg:pb-8 space-y-6 max-w-4xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground dark:text-white">Settings</h1>
              <p className="text-sm text-muted mt-1">Hotel profile configuration</p>
            </div>
            <Button onClick={handleSave} loading={saving}>
              <Save className="w-4 h-4" /> Save Changes
            </Button>
          </div>

          {/* Hotel Profile */}
          <Card>
            <CardHeader title="Hotel Profile" subtitle="Basic hotel information" action={<Badge variant="success">Active</Badge>} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={labelClass}><Hotel className="w-3.5 h-3.5 inline mr-1" />Hotel Name</label>
                <input type="text" className={inputClass} value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
              </div>
              <div>
                <label className={labelClass}><MapPin className="w-3.5 h-3.5 inline mr-1" />City</label>
                <input type="text" className={inputClass} value={formData.city} onChange={e => setFormData({...formData, city: e.target.value})} />
              </div>
              <div className="md:col-span-2">
                <label className={labelClass}>Address</label>
                <input type="text" className={inputClass} value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} />
              </div>
              <div>
                <label className={labelClass}>Star Rating</label>
                <select className={inputClass} value={formData.star_rating} onChange={e => setFormData({...formData, star_rating: Number(e.target.value)})}>
                  {[1,2,3,4,5].map(n => <option key={n} value={n}>{n} Star</option>)}
                </select>
              </div>
              <div>
                <label className={labelClass}>Total Rooms</label>
                <input type="number" className={inputClass} value={formData.total_rooms} onChange={e => setFormData({...formData, total_rooms: Number(e.target.value)})} />
              </div>
              <div>
                <label className={labelClass}>Minimum Rate (LKR)</label>
                <input type="number" className={inputClass} value={formData.minimum_rate_lkr} onChange={e => setFormData({...formData, minimum_rate_lkr: Number(e.target.value)})} />
              </div>
            </div>
          </Card>

          {/* Contact Info */}
          <Card>
            <CardHeader title="Contact Information" subtitle="Communication channels" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={labelClass}><Mail className="w-3.5 h-3.5 inline mr-1" />Email</label>
                <input type="email" className={inputClass} value={formData.contact_email} onChange={e => setFormData({...formData, contact_email: e.target.value})} />
              </div>
              <div>
                <label className={labelClass}><Phone className="w-3.5 h-3.5 inline mr-1" />Phone</label>
                <input type="tel" className={inputClass} value={formData.contact_phone} onChange={e => setFormData({...formData, contact_phone: e.target.value})} />
              </div>
              <div>
                <label className={labelClass}><Phone className="w-3.5 h-3.5 inline mr-1" />WhatsApp Number</label>
                <input type="tel" className={inputClass} value={formData.whatsapp_number} onChange={e => setFormData({...formData, whatsapp_number: e.target.value})} />
              </div>
            </div>
          </Card>

          {/* Amenities */}
          <Card>
            <CardHeader title="Amenities" subtitle="Hotel facilities" />
            <div className="flex flex-wrap gap-2">
              {selectedHotel.amenities.map((amenity, i) => (
                <Badge key={i} variant="outline" size="md">{amenity}</Badge>
              ))}
            </div>
          </Card>

          {/* Integration Status */}
          <Card>
            <CardHeader title="Integrations" subtitle="Service connections" />
            <div className="space-y-3">
              {[
                { name: "Groq AI (LLaMA 3.3)", status: "connected", icon: "🤖" },
                { name: "Supabase Database", status: "connected", icon: "🗄️" },
                { name: "Twilio WhatsApp", status: "sandbox", icon: "💬" },
                { name: "Booking.com Scraper", status: "not configured", icon: "🌐" },
              ].map((integration, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{integration.icon}</span>
                    <p className="text-sm font-medium text-foreground dark:text-white">{integration.name}</p>
                  </div>
                  <Badge variant={integration.status === "connected" ? "success" : integration.status === "sandbox" ? "warning" : "default"}>
                    {integration.status}
                  </Badge>
                </div>
              ))}
            </div>
          </Card>
        </main>
        <MobileNav />
      </div>
    </div>
  );
}
