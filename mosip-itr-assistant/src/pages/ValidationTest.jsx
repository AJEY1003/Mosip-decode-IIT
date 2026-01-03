import { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield } from 'lucide-react';

const ValidationTest = () => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-[hsl(var(--muted))]/30 to-background">
            <div className="container mx-auto px-6 py-20">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center"
                >
                    <div className="w-16 h-16 bg-[hsl(var(--gov-green))] rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <Shield className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-4xl font-bold text-[hsl(var(--foreground))] mb-4">
                        Validation Page Test
                    </h1>
                    <p className="text-[hsl(var(--muted-foreground))]">
                        This is a test validation page to check if routing works.
                    </p>
                </motion.div>
            </div>
        </div>
    );
};

export default ValidationTest;