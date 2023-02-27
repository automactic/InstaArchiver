import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {
  NbButtonModule,
  NbIconModule,
  NbLayoutModule,
  NbListModule,
  NbSidebarModule,
  NbThemeModule,
  NbUserModule,
} from '@nebular/theme';
import { NbEvaIconsModule } from '@nebular/eva-icons';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    NbButtonModule,
    NbIconModule,
    NbLayoutModule,
    NbListModule,
    NbSidebarModule.forRoot(),
    NbThemeModule.forRoot({ name: window.matchMedia("(prefers-color-scheme: dark)").matches ? 'dark' : 'default' }),
    NbUserModule,
    NbEvaIconsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
