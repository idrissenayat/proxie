import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Button from '../components/Button';
import Card from '../components/Card';
import { createRequest } from '../api/client';

const CreateRequestPage = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [form, setForm] = useState({
        description: '',
        location: '',
        budget_min: '',
        budget_max: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            // Structure matches backend expectation
            const payload = {
                consumer_id: "550e8400-e29b-41d4-a716-446655440000",
                raw_input: form.description,
                service_category: "Personal Care",
                service_type: form.description.split(' ')[0] || "Service",
                requirements: { description: form.description },
                location: { city: form.location },
                timing: { urgency: "flexible" },
                budget: {
                    min: parseFloat(form.budget_min),
                    max: parseFloat(form.budget_max),
                    currency: "USD",
                    flexibility: "somewhat_flexible"
                }
            };
            const response = await createRequest(payload);
            navigate(`/request/${response.data.id}/offers`);
        } catch (error) {
            console.error("Error creating request:", error);
            alert("Failed to create request. Is the backend running?");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col min-h-screen bg-gray-50">
            <Header title="New Service Request" showBack />

            <main className="p-4 space-y-4">
                <Card>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label>What do you need?</label>
                            <textarea
                                className="w-full border border-gray-200 rounded-xl p-3 h-24 focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="e.g. Haircut for curly hair, move-out cleaning..."
                                value={form.description}
                                onChange={(e) => setForm({ ...form, description: e.target.value })}
                                required
                            />
                        </div>

                        <div>
                            <label>Location (City)</label>
                            <input
                                type="text"
                                placeholder="e.g. Brooklyn, NY"
                                value={form.location}
                                onChange={(e) => setForm({ ...form, location: e.target.value })}
                                required
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label>Budget Min ($)</label>
                                <input
                                    type="number"
                                    placeholder="20"
                                    value={form.budget_min}
                                    onChange={(e) => setForm({ ...form, budget_min: e.target.value })}
                                    required
                                />
                            </div>
                            <div>
                                <label>Budget Max ($)</label>
                                <input
                                    type="number"
                                    placeholder="100"
                                    value={form.budget_max}
                                    onChange={(e) => setForm({ ...form, budget_max: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <Button title="Find Providers" loading={loading} />
                    </form>
                </Card>
            </main>
        </div>
    );
};

export default CreateRequestPage;
