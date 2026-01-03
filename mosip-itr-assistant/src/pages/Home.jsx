import React from 'react';
import { Hero } from '../components/Hero';
import { HowItWorks } from '../components/HowItWorks';
import { Services } from '../components/Services';
import { About } from '../components/About';
import { Contact } from '../components/Contact';

const Home = () => {
    return (
        <div className="min-h-screen bg-background text-foreground">
            <main className="relative" role="main">
                <Hero />
                <HowItWorks />
                <Services />
                <About />
                <Contact />
            </main>
        </div>
    );
};

export default Home;
