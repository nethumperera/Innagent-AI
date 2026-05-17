"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import MobileNav from "@/components/layout/MobileNav";
import ReviewCard from "@/components/reviews/ReviewCard";
import ResponseDraftEditor from "@/components/reviews/ResponseDraftEditor";
import Modal from "@/components/ui/Modal";
import Badge from "@/components/ui/Badge";
import { reviewAction } from "@/lib/api";
import type { Hotel, Review } from "@/lib/types";

const DEMO_HOTELS: Hotel[] = [
  { id: "demo-1", name: "Kandy Heritage Villa", slug: "kandy-heritage-villa", city: "Kandy", total_rooms: 12, minimum_rate_lkr: 8000, amenities: [], is_active: true, created_at: "", updated_at: "" },
];

const DEMO_REVIEWS: Review[] = [
  {
    id: "r1", hotel_id: "demo-1", platform: "Booking.com", reviewer_name: "Emma Thompson",
    star_rating: 5, review_text: "Absolutely stunning property! The Heritage Suite had breathtaking views of the Kandy hills. Chaminda at reception was incredibly helpful with our tour arrangements. The pool area is pure paradise. Will definitely return!",
    sentiment: "positive", issues_mentioned: [], urgency: "low",
    response_draft: "Dear Emma, thank you so much for your glowing review! We're thrilled that you enjoyed the Heritage Suite and its panoramic views. We'll be sure to pass on your kind words to Chaminda — he truly goes above and beyond for our guests. The pool area is indeed one of our favourite spots too! We'd love to welcome you back anytime.\n\nKandy Heritage Villa\nManaged by Co Host Ceylon",
    response_status: "draft_ready", created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: "r2", hotel_id: "demo-1", platform: "TripAdvisor", reviewer_name: "Marco Rossi",
    star_rating: 3, review_text: "The location is beautiful but the A/C in our Deluxe King room wasn't working properly on the first night. Staff fixed it by morning but we had a sweaty night. Breakfast was excellent though, especially the Sri Lankan options.",
    sentiment: "mixed", issues_mentioned: ["A/C malfunction", "delayed maintenance"], urgency: "medium",
    response_draft: "Dear Marco, thank you for taking the time to share your feedback. We sincerely apologize for the inconvenience with the air conditioning in your room. This falls below our standards, and we've since had our entire HVAC system inspected to prevent future occurrences. We're glad you enjoyed our Sri Lankan breakfast — our chef takes great pride in those authentic flavours! We hope to have the opportunity to provide you with a flawless experience next time.\n\nKandy Heritage Villa\nManaged by Co Host Ceylon",
    response_status: "draft_ready", created_at: new Date(Date.now() - 172800000).toISOString(),
  },
  {
    id: "r3", hotel_id: "demo-1", platform: "Google", reviewer_name: "Aisha Khan",
    star_rating: 2, review_text: "Disappointed with this stay. Room was not cleaned properly, found previous guest's belongings. WiFi was extremely slow. For LKR 18,000/night I expected much more.",
    sentiment: "negative", issues_mentioned: ["room cleanliness", "WiFi issues", "value for money"], urgency: "high",
    response_draft: "Dear Aisha, we are deeply sorry to hear about your experience. Finding previous guest belongings is completely unacceptable, and we have immediately reinforced our housekeeping inspection protocols. We've also upgraded our WiFi infrastructure this month. We would very much like to make this right — please contact us directly so we can discuss a resolution.\n\nKandy Heritage Villa\nManaged by Co Host Ceylon",
    response_status: "draft_ready", created_at: new Date(Date.now() - 259200000).toISOString(),
  },
];

export default function ReviewsPage() {
  const [selectedHotel] = useState<Hotel>(DEMO_HOTELS[0]);
  const [reviews, setReviews] = useState(DEMO_REVIEWS);
  const [editingReview, setEditingReview] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  const handleApprove = async (id: string) => {
    try { await reviewAction(id, "approve"); } catch {}
    setReviews(reviews.map(r => r.id === id ? { ...r, response_status: "approved" } : r));
  };

  const handleReject = async (id: string) => {
    try { await reviewAction(id, "reject"); } catch {}
    setReviews(reviews.map(r => r.id === id ? { ...r, response_status: "skipped" } : r));
  };

  const handleEditSave = async (id: string, editedResponse: string) => {
    try { await reviewAction(id, "edit", editedResponse); } catch {}
    setReviews(reviews.map(r => r.id === id ? { ...r, response_draft: editedResponse, response_status: "draft_ready" } : r));
    setEditingReview(null);
  };

  const editReview = reviews.find(r => r.id === editingReview);

  return (
    <div className="flex min-h-screen bg-background dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 lg:ml-64">
        <Header hotels={DEMO_HOTELS} selectedHotel={selectedHotel} onSelectHotel={() => {}} darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />
        <main className="p-4 md:p-6 lg:p-8 pb-24 lg:pb-8 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground dark:text-white">Reviews</h1>
              <p className="text-sm text-muted mt-1">AI-drafted review responses — approve before posting</p>
            </div>
            <div className="flex gap-2">
              <Badge variant="warning" size="md">{reviews.filter(r => r.response_status === "draft_ready").length} pending</Badge>
              <Badge variant="success" size="md">{reviews.filter(r => r.response_status === "approved").length} approved</Badge>
            </div>
          </div>

          <div className="space-y-4">
            {reviews.map((review) => (
              <ReviewCard
                key={review.id}
                review={review}
                onApprove={handleApprove}
                onEdit={(id) => setEditingReview(id)}
                onReject={handleReject}
              />
            ))}
          </div>

          {/* Edit Modal */}
          <Modal isOpen={!!editingReview} onClose={() => setEditingReview(null)} title="Edit Response Draft" size="lg">
            {editReview && (
              <ResponseDraftEditor
                initialDraft={editReview.response_draft || ""}
                reviewId={editReview.id}
                onSave={handleEditSave}
                onCancel={() => setEditingReview(null)}
              />
            )}
          </Modal>
        </main>
        <MobileNav />
      </div>
    </div>
  );
}
